import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from ingest import load_file, weekly_by_category, weekly_table

pd.set_option("display.width", 200)
settings, df = load_file("data/synthetic/taqueria.csv")
weekly = weekly_table(df, float(settings["opening_cash_balance"]))
print(weekly_by_category(df, weekly).head(8).round(0))