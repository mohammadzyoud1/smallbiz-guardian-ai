import pandas as pd
from parser import parse_file

# 1. Load and Prepare the Uploaded File

def load_file(path):

    # Parse the uploaded file and retrieve transactions, errors, and settings.

    _good, problems, settings, df = parse_file(path)

    if problems:
        raise ValueError(f"Invalid transactions: {problems[:5]}")

    # Convert transaction amounts from strings to numeric values.
    df["amount"] = pd.to_numeric(df["amount"], errors="raise")

    # Convert transaction dates into pandas datetime objects.

    df["date"] = pd.to_datetime(df["date"])
    return settings, df


# 2. Build the Weekly Cash Flow Table
def weekly_table(df, opening_cash):

    # Calculate total sales for each week.
    inflow = df[df["type"] == "sale"].set_index("date")["amount"].resample("W").sum()

    # Calculate total expenses for each week.
    outflow = df[df["type"] == "expense"].set_index("date")["amount"].resample("W").sum()

    # Combine weekly sales and expenses into one DataFrame.Replace missing values with zero when a week has no transactions.
    table = pd.DataFrame({"inflow": inflow, "outflow": outflow}).fillna(0)

    # Calculate the weekly net cash flow.
    table["net"] = table["inflow"] - table["outflow"]

    # Calculate ending cash by adding cumulative net cash flow

    table["ending_cash"] = opening_cash + table["net"].cumsum()  

    # Get the first and last transaction dates in the dataset.
    
    first_day = df["date"].min()
    last_day = df["date"].max()

    #Making sure each week starts on monday  
    full = (table.index - pd.Timedelta(days=6) >= first_day) & (table.index <= last_day)
    return table[full]


# 3. Calculate Weekly Expenses by Category

def weekly_by_category(df, weekly):

    # Keep only expense transactions.
    
    expenses = df[df["type"] == "expense"]
    # Group expenses by week and category.
    table = expenses.pivot_table(
        index=pd.Grouper(key="date", freq="W"),
        columns="category", values="amount", aggfunc="sum",
    )
    return table.reindex(weekly.index).fillna(0)

#settings, df = load_file("data/synthetic/taqueria.csv")
#weekly = weekly_table(df, float(settings["opening_cash_balance"]))
#print(len(weekly), "weeks")
#print(weekly.head(6).round(0))
#print(weekly.tail(3).round(0))