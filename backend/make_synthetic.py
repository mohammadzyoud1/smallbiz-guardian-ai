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
    "supplies_category": "supplies",
    "supplies_note":"Food supplies",
    "price_increase": (pd.Timestamp("2025-09-01"), 1.12),

}

SALON = {
    "name": "salon",
    "base_sales": 500.0,
    "sales_noise": 0.12,
    "weekday_factor": {0: 0.5, 1: 0.7, 2: 0.8, 3: 0.9, 4: 1.4, 5: 1.6, 6: 0.3},
    "season_factor": {12: 1.4},         
    "closure": None,                     
    "rent": 2200,
    "payroll": 2800,
    "utilities": 350,
    "supplies_share": 0.25,            
    "supplies_noise": 0.05,
    "supplies_category": "inventory",
    "supplies_note": "Product inventory",
    "price_increase": None,              
    "rent_increase": (pd.Timestamp("2025-10-01"), 1.1),  
    "staff_leaves": (pd.Timestamp("2026-03-01"), 0.85, 0.75),
}


def daily_sales(rng,the_business):
    days = pd.date_range(START, END, freq="D")
    closure = the_business.get("closure")
    leaves = the_business.get("staff_leaves")
    rows = []
    for day in days:
        if closure is not None and closure[0] <= day <= closure[1]:
            continue
        amount = the_business['base_sales'] * the_business["weekday_factor"].get(day.weekday()) * the_business["season_factor"].get(day.month, 1.0)
        amount = amount * rng.normal(1.0, the_business['sales_noise'])
        if leaves is not None and day >= leaves[0]:
            amount = amount * leaves[1] 
   
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
    rent_increase = the_business.get("rent_increase")
    
    leaves = the_business.get("staff_leaves")
    
    # Rent: first day of every month
    for day in pd.date_range(START, END, freq="MS"):
        rent = the_business["rent"]
        if rent_increase is not None and day >= rent_increase[0]:
            rent = rent * rent_increase[1]
        rows.append(make_row(day, "expense", "rent", rent, "Monthly rent", "yes"))

    # Payroll: every 14 days from the start date
    for day in pd.date_range(START, END, freq="14D"):
        payroll = the_business["payroll"]
        if leaves is not None and day >= leaves[0]:
            payroll = payroll * leaves[2]
        rows.append(make_row(day, "expense", "payroll", payroll, "Staff pay", "yes"))

    # Utilities: 15th of every month
    for day in pd.date_range(START, END, freq="MS"):
        pay_day = day + pd.Timedelta(days=14)
        rows.append(make_row(pay_day, "expense", "utilities", the_business["utilities"], "Utilities", "yes"))

    return pd.DataFrame(rows)


def weekly_supplies(sales, rng,  the_business):

    closure = the_business.get("closure")
    increase = the_business.get("price_increase")
    sales = sales.copy()
    sales["date"] = pd.to_datetime(sales["date"])
    rows = []
    for day in pd.date_range(START, END, freq="W-MON"):
        if closure is not None and  closure[0] <= day <= closure[1]:
            continue
        last_week = sales[(sales["date"] < day) & (sales["date"] >= day - pd.Timedelta(days=7))]
        amount = last_week["amount"].sum() * the_business["supplies_share"] * rng.normal(1.0, the_business["supplies_noise"])
        if increase is not None and day >= increase[0]:
            amount = amount * increase[1]
        if amount > 0:
            rows.append(make_row(day, "expense", the_business["supplies_category"], amount, the_business["supplies_note"], "no"))
    return pd.DataFrame(rows)


rng = np.random.default_rng(SEED)
sales = daily_sales(rng,SALON)
expenses = scheduled_expenses(SALON)
supplies = weekly_supplies(sales, rng,the_business=SALON)
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

out = all_rows.drop(columns=["month"])   

with open("data/synthetic/SALON.csv", "w", encoding="utf-8", newline="") as f:
    f.write("# opening_cash_balance=1000\n")      
    f.write("# minimum_cash_cushion=5000\n")      
    f.write("# currency=USD\n")
    f.write("# business_name=SALON \n")
    out.to_csv(f, index=False)