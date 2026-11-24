import numpy as np
import pandas as pd
from scripts.features import make_direct_table, make_features
from sklearn.ensemble import HistGradientBoostingRegressor


# 1. Backtest a Model on a Single Business
def model_backtest(weekly, folds=4, horizon=13):
    table = make_direct_table(make_features(weekly))

    # Select input features while excluding the target value and target date.
    columns = [c for c in table.columns if c not in ("target", "target_date")]
    results = []

    # Evaluate the model across multiple historical forecasting periods.
    for k in range(folds):
        # Move the testing period backwards by one forecast horizon per fold.
        end = len(weekly) - k * horizon
        # Identify the first date in the testing period.
        test_start = weekly.index[end - horizon]
        # Identify the last available week before the testing period.
        origin = weekly.index[end - horizon - 1]            

        # Use only training examples whose target dates are before the testing period to prevent future information leakage.
        train = table[table["target_date"] < test_start]
        test = table[table.index == origin]

        # Initialize the HistGradientBoosting regression model.
        model = HistGradientBoostingRegressor(random_state=42)
        model.fit(train[columns], train["target"])
        predicted = model.predict(test[columns])
        results.append(float(np.mean(np.abs(test["target"] - predicted))))
    return np.mean(results)


# 2. Global Backtesting Across Multiple Businesses

def global_backtest(weeklies, folds=4, horizon=13):
    # Generate feature tables for all businesses. Each business keeps its own historical data and target values.
    tables = {name: make_direct_table(make_features(w)) for name, w in weeklies.items()}

    # Get the feature columns from the first business's table. Exclude the target value and target date.
    columns = [c for c in next(iter(tables.values())).columns if c not in ("target", "target_date")]

    # Create an empty list of evaluation scores for each business.
    scores = {name: [] for name in weeklies}
    for k in range(folds):
        # Store training data from all businesses for this fold.
        train_parts = []
        # Collect historical training examples from every business.
        for name, w in weeklies.items():
            end = len(w) - k * horizon
            test_start = w.index[end - horizon]
            t = tables[name]
            train_parts.append(t[t["target_date"] < test_start])

        # Combine all businesses' training examples into one dataset.
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