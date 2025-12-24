import pandas as pd
from app.services.metrics_service import build_campaign_report
from app.services.forecasting_service import predict_next7days_leads
from app.utils.scoring import safe_ratio

def recommend_campaigns(start: str, end: str, country: str | None = None, top_n: int = 10):
    # 1) Historical performance
    hist = build_campaign_report(start, end, country)
    hist_map = {r["campaign_name"]: r for r in hist}

    # 2) Forecast leads
    preds = predict_next7days_leads(country=country, days=7)

    # 3) Combine
    recs = []
    for p in preds:
        camp = p["campaign_name"]
        h = hist_map.get(camp, None)

        # If no history, assume conservative conversion
        conv = (h["lead_to_enroll"] if h else 0.01)
        demo_rate = (h["lead_to_demo"] if h else 0.08)

        expected_enroll = p["predicted_leads_next7"] * conv

        # Final recommendation score
        # predicted leads + expected enroll + demo strength
        score = (
            0.50 * p["predicted_leads_next7"] +
            0.40 * expected_enroll * 100 +   # scale
            0.10 * demo_rate * 100
        )

        recs.append({
            "campaign_name": camp,
            "predicted_leads_next7": round(p["predicted_leads_next7"], 2),
            "expected_enroll_next7": round(expected_enroll, 2),
            "historical_lead_to_enroll": round(conv, 4),
            "historical_lead_to_demo": round(demo_rate, 4),
            "recommend_score": round(score, 2),
            "why": (
                "High predicted lead volume + good conversion history"
                if h and conv >= 0.02 else
                "High predicted leads, conversion needs improvement"
            )
        })

    recs.sort(key=lambda x: x["recommend_score"], reverse=True)
    return recs[:top_n]
