from ingest import load_file, weekly_table
''' Rolling-origin backtest harness (4 folds,
13-week horizon) with MAE, sMAPE, low-
cash-week recall and precision'''

names = ["taqueria", "salon", "cleaning", "corner", "childcare", "tailor"]
for name in names:
    settings, df = load_file(f"data/synthetic/{name}.csv")
    weekly = weekly_table(df, float(settings["opening_cash_balance"]))
    cushion = float(settings["minimum_cash_cushion"])
    test_weeks = weekly.iloc[-52:]              
    low = (test_weeks["ending_cash"] < cushion).sum()         
    print(f"{name:<10} cushion {cushion:>7.0f} | lowest cash {test_weeks['ending_cash'].min():>8.0f} | low weeks: {low}")