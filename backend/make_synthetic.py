import numpy as np
import pandas as pd

SEED = 42
START = "2025-01-01"
END = "2026-06-30"

# Day-of-week factors: Monday = 0 ... Sunday = 6
WEEKDAY_FACTOR = {0: 0.8, 1: 0.8, 2: 0.85, 3: 0.95, 4: 1.2, 5: 1.4, 6: 1.2}

# Month factors: summer high, January low
def season_factor(month: int) -> float:
    if month in (6, 7, 8):
        return 1.15
    if month == 1:
        return 0.8
    return 1.0


def daily_sales(rng, base=900.0):
    days = pd.date_range(START, END, freq="D")
    rows = []
    for day in days:
        amount = base * WEEKDAY_FACTOR[day.weekday()] * season_factor(day.month)
        amount = amount * rng.normal(1.0, 0.1)    # 0.1 noise size
   
        rows.append({
            "date": day.strftime("%Y-%m-%d"),
            "type": "sale",
            "category": "sales",
            "amount": round(max(amount, 0), 2),
            "note": "Daily sales",
            "recurring": "no",
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    sales = daily_sales(rng)
    print(sales.head(43))
    print(len(sales), "rows")
    print(sales["amount"].describe())