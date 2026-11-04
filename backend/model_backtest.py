import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
import pandas as pd

from scripts.features import make_features, make_direct_table

def model_backtest(weekly, folds=4, horizon=13):
    table = make_direct_table(make_features(weekly))
    columns = [c for c in table.columns if c not in ("target", "target_date")]
    results = []
    for k in range(folds):
        end = len(weekly) - k * horizon
        test_start = weekly.index[end - horizon]
        origin = weekly.index[end - horizon - 1]            
        train = table[table["target_date"] < test_start]
        test = table[table.index == origin]
        model = HistGradientBoostingRegressor(random_state=42)
        model.fit(train[columns], train["target"])
        predicted = model.predict(test[columns])
        results.append(float(np.mean(np.abs(test["target"] - predicted))))
    return np.mean(results)


def global_backtest(weeklies, folds=4, horizon=13):
    tables = {name: make_direct_table(make_features(w)) for name, w in weeklies.items()}
    columns = [c for c in next(iter(tables.values())).columns if c not in ("target", "target_date")]
    scores = {name: [] for name in weeklies}
    for k in range(folds):
        train_parts = []
        for name, w in weeklies.items():
            end = len(w) - k * horizon
            test_start = w.index[end - horizon]
            t = tables[name]
            train_parts.append(t[t["target_date"] < test_start])
        train = pd.concat(train_parts)
        model = HistGradientBoostingRegressor(random_state=42)
        model.fit(train[columns], train["target"])
        for name, w in weeklies.items():
            end = len(w) - k * horizon
            origin = w.index[end - horizon - 1]
            test = tables[name][tables[name].index == origin]
            predicted = model.predict(test[columns])
            scores[name].append(float(np.mean(np.abs(test["target"] - predicted))))
    return {name: np.mean(v) for name, v in scores.items()}


if __name__ == "__main__":
    from ingest import load_file, weekly_by_category, weekly_table

    for name in ["taqueria", "salon", "cleaning", "corner", "childcare", "tailor"]:
        settings, df = load_file(f"data/synthetic/{name}.csv")
        weekly = weekly_table(df, float(settings["opening_cash_balance"]))
        weekly = weekly.join(weekly_by_category(df, weekly))        
        print(name, round(model_backtest(weekly), 0))

    weeklies = {}
    for name in ["taqueria", "salon", "cleaning", "corner", "childcare", "tailor"]:
        settings, df = load_file(f"data/synthetic/{name}.csv")
        w = weekly_table(df, float(settings["opening_cash_balance"]))
        weeklies[name] = w.join(weekly_by_category(df, w))
    print({k: round(v, 0) for k, v in global_backtest(weeklies).items()})