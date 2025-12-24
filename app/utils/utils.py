
from datetime import date, datetime
from decimal import Decimal
import os
from typing import List, Optional
from joblib import load
import pandas as pd
from app.config.dbconnect import get_connection
import re

SESSION_STATE = {} 

def to_date(d):
    if isinstance(d, date):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return date.fromisoformat(d)
    raise TypeError(f"Invalid date type: {type(d)}")

def _safe_ratio(num, den) -> float:
    num = float(num or 0)
    den = float(den or 0)
    if den == 0:
        return 0.0
    return num / den

def _query_df(sql: str, params=()) -> pd.DataFrame:
    """Helper: run a query and return a DataFrame."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        # print("==== CAMPAIGN → COUNSELOR QUERY ====")
        # print(sql)
        # print("PARAMS:", params)
        cur.execute(sql, params)
        rows = cur.fetchall()
        return pd.DataFrame(rows)
    finally:
        cur.close()
        conn.close()

def sanitize_params(sql: str, params):
    """
    Ensure params match SQL placeholders.

    - If params is not dict → return as-is
    - If dict → remove unused keys
    """
    if not isinstance(params, dict):
        # 🔥 list / tuple / None → do nothing
        return params

    clean = {}
    for k, v in params.items():
        if f"%({k})s" in sql:
            clean[k] = v

    return clean

def df_to_rows(df):
    """
    Convert pandas DataFrame to List[dict] safely
    """
    if df is None or df.empty:
        return []

    return df.to_dict(orient="records")     


def _to_df(raw):
    """
    HARD GUARD:
    - list → DataFrame
    - DataFrame → as is
    - None / empty → empty DataFrame
    """
    if raw is None:
        return pd.DataFrame()
    if isinstance(raw, list):
        return pd.DataFrame(raw)
    if isinstance(raw, pd.DataFrame):
        return raw
    raise TypeError(f"Unsupported data type: {type(raw)}")   

def _safe(v, default=0.0):
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def compute_weight(rr: dict) -> float:
    """
    Compute a single performance weight for campaign/counselor row.
    Higher weight = better performance.
    """

    # ----------------------------
    # RAW INPUTS
    # ----------------------------
    leads = _safe(rr.get("leads"))
    demos = _safe(rr.get("demos"))
    enrollments = _safe(rr.get("enrollments"))
    spend = _safe(rr.get("spend"))

    # ----------------------------
    # DERIVED METRICS
    # ----------------------------
    lead_to_enroll = enrollments / leads if leads > 0 else 0.0
    demo_to_enroll = enrollments / demos if demos > 0 else 0.0

    cpl = spend / leads if leads > 0 else 0.0
    cpe = spend / enrollments if enrollments > 0 else 0.0

    # ----------------------------
    # SCORE COMPONENTS
    # ----------------------------

    # 1️⃣ Enrollment power (most important)
    score_enroll = enrollments * 10

    # 2️⃣ Conversion quality
    score_conversion = (
        lead_to_enroll * 50 +
        demo_to_enroll * 30
    )

    # 3️⃣ Lead scale (softened)
    score_leads = (leads ** 0.5) * 2 if leads > 0 else 0.0

    # 4️⃣ Spend penalty (only if paid)
    if spend > 0:
        penalty_spend = (cpl * 2) + (cpe * 3)
    else:
        penalty_spend = 0.0  # organic/offline

    # ----------------------------
    # FINAL WEIGHT
    # ----------------------------
    weight = (
        score_enroll +
        score_conversion +
        score_leads -
        penalty_spend
    )

    return round(weight, 2)


def enrich_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        rr = r   # ✅ already dict
        leads = rr.get("leads", 0) or 0
        demos = rr.get("demos", 0) or 0
        enr   = rr.get("enrollments", 0) or 0
        spend = rr.get("spend", 0) or 0

        rr["demo_rate"] = _safe_ratio(demos, leads)
        rr["enroll_rate"] = _safe_ratio(enr, leads)
        rr["demo_to_enroll"] = _safe_ratio(enr, demos)
        rr["cpl"] = _safe_ratio(spend, leads)
        rr["cpe"] = _safe_ratio(spend, enr)
        rr["weight"] = compute_weight(rr)

        out.append(rr)
    return out

def paginate(rows: List[dict], page: int, page_size: int) -> dict:
    total = len(rows)
    page = max(1, int(page))
    page_size = min(50, max(5, int(page_size)))
    print(page_size)
    start = (page - 1) * page_size
    end = start + page_size
    slice_rows = rows[start:end]

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "has_next": end < total,
        "next_page": page + 1 if end < total else None,
        "items": slice_rows
    }

def detect_waste(rows: List[dict], min_spend: float = 500.0) -> List[dict]:
    """
    Budget waste: high spend, low enrollments, high CPE
    """
    waste = []
    for r in rows:
        spend = float(r.get("spend", 0) or 0)
        enr = float(r.get("enrollments", 0) or 0)
        cpe = r.get("cpe", None)
        cpe_val = float(cpe) if cpe is not None else None

        if spend >= min_spend and enr <= 1:
            waste.append(r)
        elif cpe_val is not None and cpe_val >= 2000 and spend >= min_spend:
            waste.append(r)

    # worst first: spend desc
    waste.sort(key=lambda x: float(x.get("spend", 0) or 0), reverse=True)
    return waste[:10]

def json_default(o):
    if isinstance(o, Decimal):
        return float(o)   # ya str(o) if you want exact
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    return str(o)

def enforce_year_range(user_message: str, args: dict):
    text = user_message.lower()

    # year explicitly mentioned
    m = re.search(r"\byear\s+(20\d{2})\b", text)
    if not m:
        m = re.search(r"\bin\s+(20\d{2})\b", text)

    if m:
        year = m.group(1)
        args["start_date"] = f"{year}-01-01"
        args["end_date"]   = f"{year}-12-31"

    return args

def normalize_param(v):
    if v is None:
        return None
    if isinstance(v, str) and v.strip().lower() in ("", "all", "any"):
        return None
    return v

def normalize_country(value: Optional[str]) -> Optional[str]:
    """
    Normalize country name safely.

    Rules:
    - None / "" / whitespace → None
    - "ALL", "Any", "All Countries" → None
    - Known aliases → Standard country name
    - Unknown text → Title-cased original
    """

    # 🔥 HARD GUARD: None or empty
    if value is None:
        return None

    if not isinstance(value, str):
        return None

    value = value.strip()
    if value == "":
        return None

    # 🔥 Handle ALL / ANY cases
    if value.lower() in ("all", "any", "all countries", "any country"):
        return None

    # normalize for mapping lookup
    v = value.lower()
    v = re.sub(r"[^a-z]", "", v)

    mapping = {
        # UAE
        "uae": "United Arab Emirates",
        "unitedarabemirates": "United Arab Emirates",
        "emirates": "United Arab Emirates",
        "dubai": "United Arab Emirates",
        "abudhabi": "United Arab Emirates",

        # USA
        "usa": "United States",
        "unitedstates": "United States",
        "america": "United States",
        "us": "United States",

        # UK
        "uk": "United Kingdom",
        "unitedkingdom": "United Kingdom",
        "england": "United Kingdom",

        # Saudi
        "ksa": "Saudi Arabia",
        "saudiarabia": "Saudi Arabia",
        "saudi": "Saudi Arabia",
    }

    # 🔥 Return mapped value OR clean title-cased fallback
    return mapping.get(v, value.title())

def _parse_next_page(user_message: str) -> Optional[int]:
    m = re.search(r"(?:page\s*)(\d+)", user_message.lower())
    if m:
        return int(m.group(1))
    if "next" in user_message.lower():
        return -1
    return None

def json_safe(obj):
    """
    Convert non-JSON-serializable objects into safe types
    """
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)  # fallback

def safe_load_model(path):
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        return None
    try:
        return load(path)
    except Exception:
        return None