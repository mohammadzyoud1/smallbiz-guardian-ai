import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from features import make_features ,make_direct_table   
from ingest import load_file, weekly_table,weekly_by_category

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
settings, df = load_file("data/synthetic/taqueria.csv")
weekly = weekly_table(df, float(settings["opening_cash_balance"]))
weekly = weekly.join(weekly_by_category(df, weekly))
print(make_features(weekly).head(16).round(0))


table = make_direct_table(make_features(weekly))
print(len(table), "rows")
print(table.loc["2025-04-06", ["lag_1", "payroll_week", "horizon", "target_date", "target"]].head(4))