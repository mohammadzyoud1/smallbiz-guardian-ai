import pandas as pd


def load_file(path):
    settings = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                key, _, value = line[1:].strip().partition("=")
                settings[key.strip()] = value.strip()
    df = pd.read_csv(path, comment="#")
    df["date"] = pd.to_datetime(df["date"])
    return settings, df


def weekly_table(df, opening_cash):
    inflow = df[df["type"] == "sale"].set_index("date")["amount"].resample("W").sum()
    outflow = df[df["type"] == "expense"].set_index("date")["amount"].resample("W").sum()
    table = pd.DataFrame({"inflow": inflow, "outflow": outflow}).fillna(0)
    table["net"] = table["inflow"] - table["outflow"]
    table["ending_cash"] = opening_cash + table["net"].cumsum()  
    #making sure each week starts on monday  
    first_day = df["date"].min()
    last_day = df["date"].max()
    full = (table.index - pd.Timedelta(days=6) >= first_day) & (table.index <= last_day)
    return table[full]



#settings, df = load_file("data/synthetic/taqueria.csv")
#weekly = weekly_table(df, float(settings["opening_cash_balance"]))
#print(len(weekly), "weeks")
#print(weekly.head(6).round(0))
#print(weekly.tail(3).round(0))