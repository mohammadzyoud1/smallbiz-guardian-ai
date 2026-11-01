import pandas as pd


def make_features(weekly):
    f = pd.DataFrame(index=weekly.index)
    for k in [1, 2, 3, 4, 8, 12]:
        f[f"lag_{k}"] = weekly["net"].shift(k)         
    past = weekly["net"].shift(1)                          
    for w in [4, 8]:
        f[f"roll_mean_{w}"] = past.rolling(w).mean()
        f[f"roll_std_{w}"] = past.rolling(w).std() 
    f["week_of_year"] = weekly.index.isocalendar().week.values
    f["month"] = weekly.index.month
    f["payroll_week"] = (weekly["payroll"] > 0).astype(int)
    f["rent_week"] = (weekly["rent"] > 0).astype(int)      
    f["target"] = weekly["net"]
    return f


def make_direct_table(f, horizons=range(1, 14)):
    history_cols = [c for c in f.columns if c.startswith(("lag_", "roll_"))]
    calendar_cols = ["week_of_year", "month", "payroll_week", "rent_week"]
    pieces = []
    for h in horizons:
        part = f[history_cols].copy()
        for c in calendar_cols:
            part[c] = f[c].shift(-(h - 1))
        part["horizon"] = h
        part["target_date"] = f.index + pd.Timedelta(weeks=h - 1)
        part["target"] = f["target"].shift(-(h - 1))         
        pieces.append(part)
    return pd.concat(pieces).dropna()