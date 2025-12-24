import pandas as pd
from app.queries.queries import SQL_CAMPAIGN_METRICS, SQL_COUNSELOR_CAMPAIGN_METRICS, SQL_COUNSELOR_METRICS

from app.repository.repository import getSqlCampaignCounselorMetrics, getSqlCampaignMatrix, getSqlCounselorMatrix
from app.utils.scoring import campaign_score, counselor_score, safe_ratio
from app.utils.utils import _query_df, _to_df, df_to_rows

def build_campaign_report(start: str, end: str, country: str | None = None):
     
    sql, params=getSqlCampaignMatrix(SQL_CAMPAIGN_METRICS, {
        "start_date": start,
        "end_date": end,
        "country": country,
    })

    rows = _query_df(sql, params)
    df=_to_df(rows)


    if df.empty:
        return []

    REQUIRED = {"leads", "demos", "enrollments"}
    if not REQUIRED.issubset(df.columns):
        raise ValueError(f"Missing columns in campaign data: {REQUIRED - set(df.columns)}")

    df["lead_to_demo"] = df.apply(lambda r: safe_ratio(r["demos"], r["leads"]), axis=1)
    df["demo_to_enroll"] = df.apply(lambda r: safe_ratio(r["enrollments"], r["demos"]), axis=1)
    df["lead_to_enroll"] = df.apply(lambda r: safe_ratio(r["enrollments"], r["leads"]), axis=1)

    df["score"] = df.apply(campaign_score, axis=1)

    df = df.sort_values(
        ["score", "enrollments", "leads"],
        ascending=False
    )

    return df.to_dict(orient="records")

def build_counselor_report(start: str, end: str, country: str | None = None):
    sql, params = getSqlCounselorMatrix(SQL_COUNSELOR_METRICS, {
        "start_date": start,
        "end_date": end,
        "country": country,
    })
    rows = _query_df(sql, params)
    df=_to_df(rows)

    if df.empty:
        return []

    REQUIRED = {"leads", "demos", "enrollments"}
    if not REQUIRED.issubset(df.columns):
        raise ValueError(f"Missing columns in counselor data: {REQUIRED - set(df.columns)}")

    df["lead_to_demo"] = df.apply(lambda r: safe_ratio(r["demos"], r["leads"]), axis=1)
    df["lead_to_enroll"] = df.apply(lambda r: safe_ratio(r["enrollments"], r["leads"]), axis=1)

    df["score"] = df.apply(counselor_score, axis=1)

    df = df.sort_values(
        ["score", "enrollments", "leads"],
        ascending=False
    )

    return df.to_dict(orient="records")

def build_campaign_counselor_report(start: str, end: str, country: str | None = None):
    sql, params = getSqlCampaignCounselorMetrics(SQL_COUNSELOR_CAMPAIGN_METRICS,{
        "start_date": start,
        "end_date": end,
        "country": country,
    })
    rows = _query_df(sql, params)
    df=_to_df(rows)

    if df.empty:
        return []

    REQUIRED = {"leads", "demos", "enrollments"}
    if not REQUIRED.issubset(df.columns):
        raise ValueError(f"Missing columns in campaign-counselor data: {REQUIRED - set(df.columns)}")

    df["lead_to_demo"] = df.apply(lambda r: safe_ratio(r["demos"], r["leads"]), axis=1)
    df["demo_to_enroll"] = df.apply(lambda r: safe_ratio(r["enrollments"], r["demos"]), axis=1)
    df["lead_to_enroll"] = df.apply(lambda r: safe_ratio(r["enrollments"], r["leads"]), axis=1)

    df = df.sort_values(
        ["campaign_name", "lead_to_enroll", "enrollments", "leads"],
        ascending=[True, False, False, False]
    )

    return df.to_dict(orient="records")
