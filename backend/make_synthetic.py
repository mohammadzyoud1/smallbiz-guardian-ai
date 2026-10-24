import numpy as np
import pandas as pd
import os
SEED = 42
START = "2025-01-01"
END = "2026-06-30"
def make_taqueria():

    TAQUERIA = {
        "name": "taqueria2",
        "opening_cash": 1000,
        "cushion": 11000,
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
    def daily_sales(rng,the_business):
        days = pd.date_range(START, END, freq="D")
        closure = the_business.get("closure")
        rows = []
        
        for day in days:
            if closure is not None and closure[0] <= day <= closure[1]:
                continue
            amount = the_business['base_sales'] * the_business["weekday_factor"].get(day.weekday()) * the_business["season_factor"].get(day.month, 1.0)
            amount = amount * rng.normal(1.0, the_business['sales_noise'])
            
    
            rows.append({
                "date": day.strftime("%Y-%m-%d"),
                "type": "sale",
                "category": "sales",
                "amount": round(max(amount, 0), 2),
                "note": "Daily sales",
                "recurring": "no",
            })
        return pd.DataFrame(rows)

    
    def scheduled_expenses(the_business):
        rows = []
       

        # Rent: first day of every month
        for day in pd.date_range(START, END, freq="MS"):
            rent = the_business["rent"]
            rows.append(make_row(day, "expense", "rent", rent, "Monthly rent", "yes"))

        # Payroll: every 14 days from the start date
        for day in pd.date_range(START, END, freq="14D"):
            payroll = the_business["payroll"]
            rows.append(make_row(day, "expense", "payroll", payroll, "Staff pay", "yes"))

        # Utilities: 15th of every month
        for day in pd.date_range(START, END, freq="MS"):
            pay_day = day + pd.Timedelta(days=14)
            rows.append(make_row(pay_day, "expense", "utilities", the_business["utilities"], "Utilities", "yes"))

        return pd.DataFrame(rows)
    def weekly_supplies(sales, rng,  the_business):
        increase = the_business.get("price_increase")

        closure = the_business.get("closure")
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
    def print_raws():
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
        return TAQUERIA, summary,all_rows
    return print_raws()
    
def make_salon():
    SALON = {
        "name": "salon2",
        "opening_cash": 1000,
        "cushion": 5000,
        "base_sales": 500.0,
        "sales_noise": 0.12,
        "weekday_factor": {0: 0.5, 1: 0.7, 2: 0.8, 3: 0.9, 4: 1.4, 5: 1.6, 6: 0.3},
        "season_factor": {12: 1.4},         
        "rent": 2200,
        "payroll": 2800,
        "utilities": 350,
        "supplies_share": 0.25,            
        "supplies_noise": 0.05,
        "supplies_category": "inventory",
        "supplies_note": "Product inventory",
        "rent_increase": (pd.Timestamp("2025-10-01"), 1.1),  
        "staff_leaves": (pd.Timestamp("2026-03-01"), 0.85, 0.75),
    }


    def daily_sales(rng,the_business):
        days = pd.date_range(START, END, freq="D")
    
        leaves = the_business.get("staff_leaves")
        rows = []
        for day in days:
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
    
        
        sales = sales.copy()
        sales["date"] = pd.to_datetime(sales["date"])
        rows = []
        for day in pd.date_range(START, END, freq="W-MON"):
            
            last_week = sales[(sales["date"] < day) & (sales["date"] >= day - pd.Timedelta(days=7))]
            amount = last_week["amount"].sum() * the_business["supplies_share"] * rng.normal(1.0, the_business["supplies_noise"])
            
            if amount > 0:
                rows.append(make_row(day, "expense", the_business["supplies_category"], amount, the_business["supplies_note"], "no"))
        return pd.DataFrame(rows)
    def print_raws():
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
            return SALON, summary,all_rows
    return print_raws()


def make_cleaning():
    CLEANING = {
        "name": "cleaning",
        "opening_cash": 8000,
        "cushion": 9000,
        "base_sales": 420.0,
        "sales_noise": 0.08,
        "weekday_factor": {0: 1.1, 1: 1.1, 2: 1.0, 3: 1.0, 4: 1.1, 5: 0.5, 6: 0.1},
        "season_factor": {},
        "rent": 1200,
        "payroll": 4200,
        "utilities": 250,
        "supplies_share": 0.10,
        "supplies_noise": 0.05,
        "supplies_category": "supplies",
        "supplies_note": "Cleaning supplies",
    }


    def daily_sales(rng,the_business):
        days = pd.date_range(START, END, freq="D")
    
       
        rows = []
        for day in days:
            amount = the_business['base_sales'] * the_business["weekday_factor"].get(day.weekday()) * the_business["season_factor"].get(day.month, 1.0)
            amount = amount * rng.normal(1.0, the_business['sales_noise']) 
       
            rows.append({
                "date": day.strftime("%Y-%m-%d"),
                "type": "sale",
                "category": "sales",
                "amount": round(max(amount, 0), 2),
                "note": "Daily sales",
                "recurring": "no",
            })
        return pd.DataFrame(rows)
    def scheduled_expenses(the_business):
        rows = []
       

        # Rent: first day of every month
        for day in pd.date_range(START, END, freq="MS"):
            rent = the_business["rent"]
            
            rows.append(make_row(day, "expense", "rent", rent, "Monthly rent", "yes"))

        # Payroll: every 14 days from the start date
        for day in pd.date_range(START, END, freq="14D"):
            payroll = the_business["payroll"]
            
            rows.append(make_row(day, "expense", "payroll", payroll, "Staff pay", "yes"))

        # Utilities: 15th of every month
        for day in pd.date_range(START, END, freq="MS"):
            pay_day = day + pd.Timedelta(days=14)
            rows.append(make_row(pay_day, "expense", "utilities", the_business["utilities"], "Utilities", "yes"))

        return pd.DataFrame(rows)

    def weekly_supplies(sales, rng,  the_business):
    
        
        sales = sales.copy()
        sales["date"] = pd.to_datetime(sales["date"])
        rows = []
        for day in pd.date_range(START, END, freq="W-MON"):
            
            last_week = sales[(sales["date"] < day) & (sales["date"] >= day - pd.Timedelta(days=7))]
            amount = last_week["amount"].sum() * the_business["supplies_share"] * rng.normal(1.0, the_business["supplies_noise"])
            
            if amount > 0:
                rows.append(make_row(day, "expense", the_business["supplies_category"], amount, the_business["supplies_note"], "no"))
        return pd.DataFrame(rows)
    def van_repair():
        row = make_row(pd.Timestamp("2025-07-15"), "expense", "equipment", 2400, "Van repair", "no")
        return pd.DataFrame([row])
    def commercial_income():
        rows = []
        # one bill at the end of each month, starting Nov 2024 so Jan 2025 already gets a payment
        for bill_day in pd.date_range("2024-11-30", END, freq="ME"):
            wait = 45
            if bill_day == pd.Timestamp("2025-10-31"):
                wait = wait + 30
            pay_day = bill_day + pd.Timedelta(days=wait)
            if pay_day <= pd.Timestamp(END):
                rows.append(make_row(pay_day, "sale", "sales", 3500, "Commercial client payment", "yes"))
        return pd.DataFrame(rows)
    def print_raws():
            rng = np.random.default_rng(SEED)
            sales = daily_sales(rng,CLEANING)
            expenses = scheduled_expenses(CLEANING)
            supplies = weekly_supplies(sales, rng,the_business=CLEANING)
            all_rows = pd.concat([sales, expenses, supplies,van_repair(),commercial_income()], ignore_index=True)
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
            return CLEANING, summary,all_rows
    return print_raws()

def make_corner():
    CORNER = {
        "name": "corner",
        "opening_cash": 7000,
        "cushion": 9000,
        "base_sales": 700.0,
        "sales_noise": 0.07,
        "weekday_factor": {0: 0.95, 1: 0.95, 2: 0.95, 3: 1.0, 4: 1.1, 5: 1.1, 6: 0.95},
        "season_factor": {},
        "rent": 2500,
        "payroll": 2600,
        "utilities": 450,
        "utilities_factor": {12: 1.5, 1: 1.5, 2: 1.5, 6: 1.4, 7: 1.4, 8: 1.4},
        "supplies_share": 0.55,
        "supplies_noise": 0.05,
        "supplies_category": "inventory",
        "supplies_note": "Stock purchase",
        "dip": (pd.Timestamp("2025-11-03"), pd.Timestamp("2025-11-23"), 0.7),
    }


    def daily_sales(rng,the_business):
        days = pd.date_range(START, END, freq="D")

        rows = []
        dip = the_business.get("dip")
        for day in days:
            amount = the_business['base_sales'] * the_business["weekday_factor"].get(day.weekday()) * the_business["season_factor"].get(day.month, 1.0)
            amount = amount * rng.normal(1.0, the_business['sales_noise'])
            if dip is not None and dip[0] <= day <= dip[1]:
                amount = amount * dip[2]
       
            rows.append({
                "date": day.strftime("%Y-%m-%d"),
                "type": "sale",
                "category": "sales",
                "amount": round(max(amount, 0), 2),
                "note": "Daily sales",
                "recurring": "no",
            })
        return pd.DataFrame(rows)
    def scheduled_expenses(the_business):
        rows = []
       

        # Rent: first day of every month
        for day in pd.date_range(START, END, freq="MS"):
            rent = the_business["rent"]
            
            rows.append(make_row(day, "expense", "rent", rent, "Monthly rent", "yes"))

        # Payroll: every 14 days from the start date
        for day in pd.date_range(START, END, freq="14D"):
            payroll = the_business["payroll"]
            
            rows.append(make_row(day, "expense", "payroll", payroll, "Staff pay", "yes"))

        # Utilities: 15th of every month
        for day in pd.date_range(START, END, freq="MS"):
            pay_day = day + pd.Timedelta(days=14)
            utilities = the_business["utilities"] * the_business["utilities_factor"].get(day.month, 1.0)
            rows.append(make_row(pay_day, "expense", "utilities", the_business["utilities"], "Utilities", "yes"))

        return pd.DataFrame(rows)

    def weekly_supplies(sales, rng,  the_business):
    
        
        sales = sales.copy()
        sales["date"] = pd.to_datetime(sales["date"])
        rows = []
        buy_days = pd.date_range(START, END, freq="W-MON").union(
            pd.date_range(START, END, freq="W-THU")
        )
        for day in buy_days:
            
            last_week = sales[(sales["date"] < day) & (sales["date"] >= day - pd.Timedelta(days=7))]
            amount = last_week["amount"].sum() * (the_business["supplies_share"]/2) * rng.normal(1.0, the_business["supplies_noise"])
            
            if amount > 0:
                rows.append(make_row(day, "expense", the_business["supplies_category"], amount, the_business["supplies_note"], "no"))
        return pd.DataFrame(rows)
   
    def print_raws():
            rng = np.random.default_rng(SEED)
            sales = daily_sales(rng,CORNER)
            expenses = scheduled_expenses(CORNER)
            supplies = weekly_supplies(sales, rng,the_business=CORNER)
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
            return all_rows,CORNER, summary,
    return print_raws()


def make_childcare():
    CHILDCARE = {
        "name": "childcare",
        "opening_cash": 6000,
        "cushion": 8000,
        "families": 14,
        "summer_families": 11,
        "tuition": 650,
        "rent": 2400,
        "payroll": 3200,
        "utilities": 400,
        "subsidy": 2800,
        "family_leaves": (pd.Timestamp("2026-01-01"), 1),
    }


    
    def scheduled_expenses(the_business):
        rows = []
        # Rent: first day of every month
        for day in pd.date_range(START, END, freq="MS"):
            rent = the_business["rent"]
            
            rows.append(make_row(day, "expense", "rent", rent, "Monthly rent", "yes"))

        # Payroll: every 14 days from the start date
        for day in pd.date_range(START, END, freq="14D"):
            payroll = the_business["payroll"]
            
            rows.append(make_row(day, "expense", "payroll", payroll, "Staff pay", "yes"))

        # Utilities: 15th of every month
        for day in pd.date_range(START, END, freq="MS"):
            pay_day = day + pd.Timedelta(days=14)
            rows.append(make_row(pay_day, "expense", "utilities", the_business["utilities"], "Utilities", "yes"))

        return pd.DataFrame(rows)
    def tuition_income(the_business):
        rows = []
        leaves = the_business.get("family_leaves")
        for day in pd.date_range(START, END, freq="MS"):
            families = the_business["families"]
            if day.month in (6, 7, 8):
                families = the_business["summer_families"]
            if leaves is not None and day >= leaves[0]:
                families = families - leaves[1]
            rows.append(make_row(day, "sale", "sales", families * the_business["tuition"], "Monthly tuition", "yes"))
        return pd.DataFrame(rows)
    def subsidy_income(rng, the_business):
        rows = []
        for first in pd.date_range(START, END, freq="MS"):
            # arrives on a different day each month, between the 8th and the 22nd
            pay_day = first + pd.Timedelta(days=int(rng.integers(7, 22)))
            if first == pd.Timestamp("2025-08-01"):
                pay_day = pay_day + pd.Timedelta(days=42)   
            if pay_day <= pd.Timestamp(END):
                rows.append(make_row(pay_day, "sale", "other_income", the_business["subsidy"], "State subsidy payment", "no"))
        return pd.DataFrame(rows)
    
    def print_raws():
            rng = np.random.default_rng(SEED)
            tuition = tuition_income(CHILDCARE)
            subsidy = subsidy_income(rng, CHILDCARE)
            expenses = scheduled_expenses(CHILDCARE)
            all_rows = pd.concat([ expenses,tuition,subsidy], ignore_index=True)
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
            return all_rows ,CHILDCARE, summary
    return print_raws()

def make_tailor():
    TAILOR = {
        "name": "tailor",
        "opening_cash": 5000,
        "cushion": 4500,
        "base_sales": 380.0,
        "sales_noise": 0.15,
        "weekday_factor": {0: 0.8, 1: 0.9, 2: 0.9, 3: 1.0, 4: 1.2, 5: 1.4, 6: 0.5},
        # slow February, school start (Aug, Sep), holidays (Nov, Dec)
        "season_factor": {2: 0.7, 8: 1.25, 9: 1.15, 11: 1.3, 12: 1.4},
        # wedding-season surge in month 17 (May 2026): first day, last day, multiplier
        "surge": (pd.Timestamp("2026-05-01"), pd.Timestamp("2026-05-31"), 1.4),
        "rent": 1700,
        "payroll": 2400,
        "utilities": 250,
        "supplies_share": 0.22,
        "supplies_noise": 0.05,
        "supplies_category": "supplies",
        "supplies_note": "Fabric and thread",
        # sewing machine failure in month 6 (June 2025): date and cost
        "machine_failure": (pd.Timestamp("2025-06-10"), 900),
    }

    def daily_sales(rng, the_business):
        days = pd.date_range(START, END, freq="D")
        surge = the_business.get("surge")
        rows = []
        for day in days:
            amount = (
                the_business["base_sales"]
                * the_business["weekday_factor"].get(day.weekday())
                * the_business["season_factor"].get(day.month, 1.0)
            )
            amount = amount * rng.normal(1.0, the_business["sales_noise"])
            if surge is not None and surge[0] <= day <= surge[1]:
                amount = amount * surge[2]
            rows.append({
                "date": day.strftime("%Y-%m-%d"),
                "type": "sale",
                "category": "sales",
                "amount": round(max(amount, 0), 2),
                "note": "Daily sales",
                "recurring": "no",
            })
        return pd.DataFrame(rows)

    def scheduled_expenses(the_business):
        rows = []
        # Rent: first day of every month
        for day in pd.date_range(START, END, freq="MS"):
            rent = the_business["rent"]
            rows.append(make_row(day, "expense", "rent", rent, "Monthly rent", "yes"))
        # Payroll: every 14 days
        for day in pd.date_range(START, END, freq="14D"):
            payroll = the_business["payroll"]
            rows.append(make_row(day, "expense", "payroll", payroll, "Staff pay", "yes"))
        # Utilities: 15th of every month
        for day in pd.date_range(START, END, freq="MS"):
            pay_day = day + pd.Timedelta(days=14)
            rows.append(make_row(pay_day, "expense", "utilities", the_business["utilities"], "Utilities", "yes"))
        return pd.DataFrame(rows)

    def weekly_supplies(sales, rng, the_business):
        sales = sales.copy()
        sales["date"] = pd.to_datetime(sales["date"])
        rows = []
        for day in pd.date_range(START, END, freq="W-MON"):
            last_week = sales[(sales["date"] < day) & (sales["date"] >= day - pd.Timedelta(days=7))]
            amount = last_week["amount"].sum() * the_business["supplies_share"] * rng.normal(1.0, the_business["supplies_noise"])
            if amount > 0:
                rows.append(make_row(day, "expense", the_business["supplies_category"], amount, the_business["supplies_note"], "no"))
        return pd.DataFrame(rows)

    def small_equipment(rng):
        # a small tool purchase (scissors, needles, pressing cloth...) every two months
        rows = []
        for first in pd.date_range(START, END, freq="2MS"):
            day = first + pd.Timedelta(days=int(rng.integers(3, 25)))
            amount = float(rng.uniform(60, 160))
            rows.append(make_row(day, "expense", "equipment", amount, "Small equipment", "no"))
        return pd.DataFrame(rows)

    def machine_failure(the_business):
        day, cost = the_business["machine_failure"]
        return pd.DataFrame([make_row(day, "expense", "equipment", cost, "Sewing machine replacement", "no")])

    def print_raws():
        rng = np.random.default_rng(SEED)
        sales = daily_sales(rng, TAILOR)
        expenses = scheduled_expenses(TAILOR)
        supplies = weekly_supplies(sales, rng, TAILOR)
        small = small_equipment(rng)
        failure = machine_failure(TAILOR)
        all_rows = pd.concat([sales, expenses, supplies, small, failure], ignore_index=True)
        all_rows = all_rows.sort_values("date").reset_index(drop=True)
        print(len(all_rows), "rows")
        all_rows["month"] = all_rows["date"].str[:7]
        summary = all_rows.pivot_table(
            index="month", columns="type", values="amount", aggfunc="sum"
        )
        summary["net"] = summary["sale"] - summary["expense"]
        print(summary.round(0))
        return  all_rows,TAILOR, summary

    return print_raws()

def make_row(date, type_, category, amount, note, recurring):
    return {
        "date": date.strftime("%Y-%m-%d"),
        "type": type_,
        "category": category,
        "amount": round(amount, 2),
        "note": note,
        "recurring": recurring,
    }


all_rows,category,summary=make_tailor()
#make_childcare()
def extract_csv(all_rows,business):
    os.makedirs("data/synthetic", exist_ok=True)

    out = all_rows.drop(columns=["month"])   
    path=f"data/synthetic/{business['name']}.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(f"# opening_cash_balance={business['opening_cash']}\n")      
        f.write(f"# minimum_cash_cushion={business['cushion']}\n")      
        f.write("# currency=USD\n")
        f.write(f"# business_name={business['name']} \n")
        out.to_csv(f, index=False)
extract_csv(all_rows,category)


#def scheduled_expenses(the_business):
#    rows = []
#    rent_increase = the_business.get("rent_increase")
#    
#    leaves = the_business.get("staff_leaves")
#    
#    # Rent: first day of every month
#    for day in pd.date_range(START, END, freq="MS"):
#        rent = the_business["rent"]
#        if rent_increase is not None and day >= rent_increase[0]:
#            rent = rent * rent_increase[1]
#        rows.append(make_row(day, "expense", "rent", rent, "Monthly rent", "yes"))
#
#    # Payroll: every 14 days from the start date
#    for day in pd.date_range(START, END, freq="14D"):
#        payroll = the_business["payroll"]
#        if leaves is not None and day >= leaves[0]:
#            payroll = payroll * leaves[2]
#        rows.append(make_row(day, "expense", "payroll", payroll, "Staff pay", "yes"))
#
#    # Utilities: 15th of every month
#    for day in pd.date_range(START, END, freq="MS"):
#        pay_day = day + pd.Timedelta(days=14)
#        rows.append(make_row(pay_day, "expense", "utilities", the_business["utilities"], "Utilities", "yes"))
#
#    return pd.DataFrame(rows)
#
#
#def weekly_supplies(sales, rng,  the_business):
#
#    closure = the_business.get("closure")
#    increase = the_business.get("price_increase")
#    sales = sales.copy()
#    sales["date"] = pd.to_datetime(sales["date"])
#    rows = []
#    for day in pd.date_range(START, END, freq="W-MON"):
#        if closure is not None and  closure[0] <= day <= closure[1]:
#            continue
#        last_week = sales[(sales["date"] < day) & (sales["date"] >= day - pd.Timedelta(days=7))]
#        amount = last_week["amount"].sum() * the_business["supplies_share"] * rng.normal(1.0, the_business["supplies_noise"])
#        if increase is not None and day >= increase[0]:
#            amount = amount * increase[1]
#        if amount > 0:
#            rows.append(make_row(day, "expense", the_business["supplies_category"], amount, the_business["supplies_note"], "no"))
#    return pd.DataFrame(rows)

#def print_rows(businesss):
#    rng = np.random.default_rng(SEED)
#    sales = daily_sales(rng,businesss)
#    expenses = scheduled_expenses(businesss)
#    supplies = weekly_supplies(sales, rng,the_business=businesss)
#    all_rows = pd.concat([sales, expenses, supplies], ignore_index=True)
#    all_rows = all_rows.sort_values("date").reset_index(drop=True)
#    print(all_rows.head(12))
#    print(len(all_rows), "rows")
#    print("------------------------------")
#    # Monthly check: money in vs money out
#    all_rows["month"] = all_rows["date"].str[:7]
#    summary = all_rows.pivot_table(
#        index="month", columns="type", values="amount", aggfunc="sum"
#    )
#    print(summary)
#    summary["net"] = summary["sale"] - summary["expense"]
#    print(summary.round(0))
