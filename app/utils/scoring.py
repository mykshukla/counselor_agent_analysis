from decimal import Decimal
import numpy as np

def safe_ratio(a, b):
    return float(a) / float(b) if b else 0.0

def campaign_score(row):
    leads = as_float(row.get("leads"))
    demos = as_float(row.get("demos"))
    enrollments = as_float(row.get("enrollments"))

    lead_to_demo = demos / leads if leads > 0 else 0.0
    demo_to_enroll = enrollments / demos if demos > 0 else 0.0
    lead_to_enroll = enrollments / leads if leads > 0 else 0.0

    return (
        0.35 * lead_to_demo +
        0.45 * demo_to_enroll +
        0.20 * lead_to_enroll
    )

def counselor_score(row):
    leads = as_float(row.get("leads"))
    demos = as_float(row.get("demos"))
    enrollments = as_float(row.get("enrollments"))

    lead_to_demo = enrollments / leads if leads > 0 else 0.0
    lead_to_enroll = enrollments / leads if leads > 0 else 0.0

    # ✅ SAFE float math
    volume_factor = np.tanh(leads / 50.0)

    return (
        0.45 * lead_to_enroll +
        0.25 * lead_to_demo +
        0.30 * volume_factor
    )

def as_float(x, default=0.0):
    """
    Safely convert Decimal / int / str to float
    """
    if x is None:
        return default
    if isinstance(x, Decimal):
        return float(x)
    try:
        return float(x)
    except Exception:
        return default
