import pandas as pd
import numpy as np

def make_time_features(df: pd.DataFrame, date_col="day"):
    d = pd.to_datetime(df[date_col])
    df = df.copy()
    df["dow"] = d.dt.dayofweek
    df["week"] = d.dt.isocalendar().week.astype(int)
    df["month"] = d.dt.month
    df["is_weekend"] = (df["dow"] >= 5).astype(int)

    # Rolling features (requires sorted)
    df = df.sort_values(date_col)
    df["leads_7d_avg"] = df["leads"].rolling(7, min_periods=1).mean()
    df["leads_14d_avg"] = df["leads"].rolling(14, min_periods=1).mean()
    df["leads_7d_sum"] = df["leads"].rolling(7, min_periods=1).sum()
    return df

def future_frame(last_day, days=7):
    start = pd.to_datetime(last_day) + pd.Timedelta(days=1)
    days_list = pd.date_range(start, periods=days, freq="D")
    return pd.DataFrame({"day": days_list})
