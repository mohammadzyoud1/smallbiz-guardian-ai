import numpy as np
import pandas as pd
import os
SEED = 42
START = "2025-01-01"
END = "2026-06-30"
TAQUERIA = {
    "name": "taqueria",
    "base_sales": 900.0,
    "sales_noise": 0.10,
    "weekday_factor": {0: 0.8, 1: 0.8, 2: 0.85, 3: 0.95, 4: 1.2, 5: 1.4, 6: 1.2},
    "season_factor": {1: 0.8, 6: 1.15, 7: 1.15, 8: 1.15},  # other months = 1.0
    "closure": (pd.Timestamp("2026-02-09"), pd.Timestamp("2026-02-22")),
    "rent":3000,
    "payroll":4200,
    "utilities":600,
    "supplies_share": 0.42,
    "supplies_noise": 0.05,
    "price_increase": (pd.Timestamp("2025-09-01"), 1.12),

}


def daily_sales(rng,the_business):
    days = pd.date_range(START, END, freq="D")
    rows = []
    for day in days:
        if the_business["closure"][0] <= day <= the_business["closure"][1]:
            continue
        amount = the_business['base_sales'] * the_business["weekday_factor"].get(day.weekday()) * the_business["season_factor"].get(day.month, 1.0)
        amount = amount * rng.normal(1.0, the_business['sales_noise'])    # 0.1 noise size
   
        rows.append({
            "date": day.strftime("%Y-%m-%d"),
            "type": "sale",
            "category": "sales",
            "amount": round(max(amount, 0), 2),
            "note": "Daily sales",
            "recurring": "no",
        })
    return pd.DataFrame(rows)

def make_row(date, type_, category, amount, note, recurring):
    return {
        "date": date.strftime("%Y-%m-%d"),
        "type": type_,
        "category": category,
        "amount": round(amount, 2),
        "note": note,
        "recurring": recurring,
    }


def scheduled_expenses(the_business):
    rows = []

    # Rent: first day of every month
    for day in pd.date_range(START, END, freq="MS"):
        rows.append(make_row(day, "expense", "rent", the_business['rent'], "Monthly rent", "yes"))

    # Payroll: every 14 days from the start date
    for day in pd.date_range(START, END, freq="14D"):
        rows.append(make_row(day, "expense", "payroll", the_business["payroll"], "Staff pay", "yes"))

    # Utilities: 15th of every month
    for day in pd.date_range(START, END, freq="MS"):
        pay_day = day + pd.Timedelta(days=14)
        rows.append(make_row(pay_day, "expense", "utilities", the_business["utilities"], "Utilities", "yes"))

    return pd.DataFrame(rows)


def weekly_supplies(sales, rng,  the_business):
    # Every Monday, buy supplies worth ~35% of the last 7 days of sales
    increase_date, increase_factor = the_business["price_increase"]
    sales = sales.copy()
    sales["date"] = pd.to_datetime(sales["date"])
    rows = []
    for day in pd.date_range(START, END, freq="W-MON"):
        if the_business["closure"][0] <= day <= the_business["closure"][1]:
            continue
        last_week = sales[(sales["date"] < day) & (sales["date"] >= day - pd.Timedelta(days=7))]
        amount = last_week["amount"].sum() * the_business["supplies_share"] * rng.normal(1.0, the_business["supplies_noise"])
        if day >= increase_date:
            amount = amount * increase_factor
        if amount > 0:
            rows.append(make_row(day, "expense", "supplies", amount, "Food supplies", "no"))
    return pd.DataFrame(rows)


rng = np.random.default_rng(SEED)
sales = daily_sales(rng,TAQUERIA)
expenses = scheduled_expenses(TAQUERIA)
supplies = weekly_supplies(sales, rng,the_business=TAQUERIA)
all_rows = pd.concat([sales, expenses, supplies], ignore_index=True)
all_rows = all_rows.sort_values("date").reset_index(drop=True)
print(all_rows.head(12))
print(len(all_rows), "rows")
print("------------------------------")
# Monthly check: money in vs money out
all_rows["month"] = all_rows["date"].str[:7]
summary = all_rows.pivot_table(
    index="month", columns="type", values="amount", aggfunc="sum"
)
print(summary)
summary["net"] = summary["sale"] - summary["expense"]
print(summary.round(0))

os.makedirs("data/synthetic", exist_ok=True)

out = all_rows.drop(columns=["month"])   # the helper column isn't part of the template

with open("data/synthetic/taqueria.csv", "w", encoding="utf-8", newline="") as f:
    f.write("# opening_cash_balance=1000\n")      # BLANK 1
    f.write("# minimum_cash_cushion=11000\n")      # BLANK 2
    f.write("# currency=USD\n")
    f.write("# business_name=Synthetic Taqueria\n")
    out.to_csv(f, index=False)