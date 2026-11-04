import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from band import make_band
from ingest import load_file, weekly_table

pd.set_option("display.width", 200)
settings, df = load_file("data/synthetic/taqueria.csv")
weekly = weekly_table(df, float(settings["opening_cash_balance"]))
net = weekly["net"]
point, low, high = make_band(net, net.iloc[:-13])
print(pd.DataFrame({"actual": net.iloc[-13:].values, "low": low, "forecast": point, "high": high}).round(0))