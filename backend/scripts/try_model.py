import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from features import make_direct_table, make_features
from ingest import load_file, weekly_by_category, weekly_table
from sklearn.ensemble import HistGradientBoostingRegressor

settings, df = load_file("data/synthetic/taqueria.csv")
weekly = weekly_table(df, float(settings["opening_cash_balance"]))
weekly = weekly.join(weekly_by_category(df, weekly))
table = make_direct_table(make_features(weekly))

cut = weekly.index[-13]                       
train = table[table["target_date"] < cut]
test = table[(table["target_date"] >= cut) & (table["horizon"] == 1)]

columns = [c for c in table.columns if c not in ("target", "target_date")]
model = HistGradientBoostingRegressor(random_state=42)
model.fit(train[columns], train["target"])

predicted = model.predict(test[columns])
print("test rows:", len(test))
print("model MAE:", round(float(np.mean(np.abs(test["target"] - predicted))), 0))