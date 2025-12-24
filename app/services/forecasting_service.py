import os
from pyexpat import model
import tempfile
from typing import Any, List
import pandas as pd
import numpy as np
from joblib import dump, load
from sklearn.ensemble import RandomForestRegressor
from app.config.config import settings

from app.utils.features import make_time_features, future_frame
from app.utils.utils import _query_df, normalize_country, normalize_param, safe_load_model

MODEL_PATH = os.path.join(settings.model_dir, "leads_model.joblib")



def load_daily_agg(country: str | None = None) -> pd.DataFrame:

    print(os.path.exists("data/models"))

    sql = """
    SELECT DATE(L.CREATED_DATE) AS day, L.UTM_CAMPAIGN as campaign_name, SUM(LC.TOTALLEAD) AS leads, 
    SUM(IF (LC.LEAD_TYPE='DEMO', LC.DEMODONE,0)) AS demos, SUM(LC.CONVERTED) AS enrollments, MAX(ROUND(IFNULL(LD.SPENT,0),2)) AS spend 
    FROM LEAD_DEMO_COUNT LC INNER JOIN LEADS L ON L.ID=LC.ID 
    INNER JOIN LEADS_DETAILS LD ON LD.LEAD_ID=L.ID LEFT JOIN COUNTRIES C ON C.ID=L.COUNTRY 
    WHERE LC.INTERESTED_FOR='B2C' AND L.ACTIVE_STATUS='Y' AND L.UTM_CAMPAIGN IS NOT NULL 
    AND L.UTM_CAMPAIGN NOT IN('N/A','N%2FA') AND L.UTM_SOURCE NOT IN('ig','fb','an','Test','one', 'demo','th','N%2FA')
    """

    country=normalize_param(country)
    params: List[Any] = []  
    if country:
        sql += " AND C.NAME = %s"
        params.append(normalize_country(country))
    return _query_df(sql, params)

def train_leads_model(country=None):
    df = load_daily_agg(country)

    if df.empty:
        raise ValueError("No data to train forecast model")

    df = df.fillna(0)
    df = make_time_features(df, "day")
    df["camp_hash"] = df["campaign_name"].apply(lambda x: hash(x) % 10_000)

    X = df[
        ["camp_hash", "dow", "week", "month", "is_weekend",
         "leads_7d_avg", "leads_14d_avg", "leads_7d_sum"]
    ]
    y = df["leads"]

    # ✅ ONLY sklearn estimator
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X, y)

    os.makedirs(settings.model_dir, exist_ok=True)

    # 🔥 atomic write
    with tempfile.NamedTemporaryFile(
        dir=settings.model_dir,
        delete=False
    ) as tmp:
        tmp_path = tmp.name

    dump(model, tmp_path)
    os.replace(tmp_path, MODEL_PATH)

    return {"status": "trained", "rows": len(df)}

def predict_next7days_leads(country: str | None = None, days: int = 7):
    """
    SAFE forecasting function

    - ML model optional
    - Never crashes agent
    - Falls back to rule-based forecast
    """

    df = load_daily_agg(country)
    if df is None or df.empty:
        return []

    df = df.fillna(0)

    # -----------------------------
    # 1️⃣ TRY ML MODEL (IF AVAILABLE)
    # -----------------------------
    model = safe_load_model(MODEL_PATH)

    if model is not None:
        try:
            out = []

            for camp, g in df.groupby("campaign_name"):
                g = g.sort_values("day")
                last_day = g["day"].max()

                hist = make_time_features(g, "day")
                last = hist.iloc[-1]

                fut = future_frame(last_day, days=days)
                fut["campaign_name"] = camp
                fut["camp_hash"] = hash(camp) % 10_000

                fut = make_time_features(fut.assign(leads=0), "day")

                fut["leads_7d_avg"] = float(last.get("leads_7d_avg", 0))
                fut["leads_14d_avg"] = float(last.get("leads_14d_avg", 0))
                fut["leads_7d_sum"] = float(last.get("leads_7d_sum", 0))

                Xf = fut[
                    [
                        "camp_hash",
                        "dow",
                        "week",
                        "month",
                        "is_weekend",
                        "leads_7d_avg",
                        "leads_14d_avg",
                        "leads_7d_sum",
                    ]
                ]

                preds = model.predict(Xf)
                preds = np.clip(preds, 0, None)

                out.append({
                    "campaign_name": camp,
                    "country": country,
                    "predicted_leads_next7": float(np.sum(preds)),
                    "method": "ml_model",
                    "daily": [
                        {"day": str(d.date()), "pred": float(p)}
                        for d, p in zip(fut["day"], preds)
                    ],
                })

            return sorted(out, key=lambda x: x["predicted_leads_next7"], reverse=True)

        except Exception as e:
            # 🔥 ML failed → fallback
            print("ML forecast failed, switching to rule-based:", e)

    # --------------------------------
    # 2️⃣ FALLBACK: RULE-BASED FORECAST
    # --------------------------------
    return rule_based_forecast(df, country, days)

def rule_based_forecast(df: pd.DataFrame, country: str | None, days: int):
    """
    Simple & reliable forecast:
    last 7-day average × future days
    """

    out = []

    for camp, g in df.groupby("campaign_name"):
        g = g.sort_values("day")

        avg_7 = g["leads"].tail(7).mean()
        predicted = float(avg_7 * days)

        out.append({
            "campaign_name": camp,
            "country": country,
            "predicted_leads_next7": round(predicted, 2),
            "method": "rule_based_avg_7d"
        })

    return sorted(out, key=lambda x: x["predicted_leads_next7"], reverse=True)

