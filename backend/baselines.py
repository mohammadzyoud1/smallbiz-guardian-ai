import numpy as np
from ingest import load_file, weekly_table
import pandas as pd
import mlflow

def naive(history, horizon=13):
    return np.repeat(history.iloc[-1], horizon)


def moving_average(history, horizon=13, window=4):
    return np.repeat(history.iloc[-window:].mean(), horizon)     

def seasonal_naive(history, horizon=13, season=52):
    if len(history) < season:
        season = 4
    values = history.values
    forecast = []
    for i in range(horizon):
        forecast.append(values[len(values) - season + i % season])
    return np.array(forecast)


def mae(actual, predicted):
    return np.mean(np.abs(np.array(actual) - np.array(predicted)))


def smape(actual, predicted):
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)
    denom = (np.abs(actual) + np.abs(predicted)) / 2
    denom[denom == 0] = 1
    return np.mean(np.abs(actual - predicted) / denom) * 100

def low_cash_scores(actual_net, predicted_net, cash_before, cushion):
    real_cash = cash_before + np.cumsum(np.array(actual_net))
    forecast_cash = cash_before + np.cumsum(np.array(predicted_net))
    real_low = real_cash < cushion
    forecast_low = forecast_cash < cushion          
    caught = (real_low & forecast_low).sum()
    recall = caught / real_low.sum() if real_low.sum() > 0 else np.nan
    precision = caught / forecast_low.sum() if forecast_low.sum() > 0 else np.nan
    return recall, precision


#test the simple forcast 
def backtest(net,ending_cash,cushion, folds=4, horizon=13):
    rows = []
    for k in range(folds):
        end = len(net) - (k * horizon)                  
        history = net.iloc[:(end - horizon)]                     
        actual = net.iloc[end - horizon:end]
        cash_before = ending_cash.iloc[end - horizon - 1]
        row = {}
        for label, forecast in [("naive", naive(history)),
                                ("moving_avg", moving_average(history)),
                                ("seasonal", seasonal_naive(history))]:
            row[label] = mae(actual, forecast)
            row[label + "_smape"] = smape(actual, forecast)
            recall, precision = low_cash_scores(actual, forecast, cash_before, cushion)
            row[label + "_recall"] = recall
            row[label + "_precision"] = precision
        rows.append(row)
    return pd.DataFrame(rows)
if __name__ == "__main__":
    names = ["taqueria", "salon", "cleaning", "corner", "childcare", "tailor"]
    for name in names:
        settings, df = load_file(f"data/synthetic/{name}.csv")
        weekly = weekly_table(df, float(settings["opening_cash_balance"]))
        cushion = float(settings["minimum_cash_cushion"])
        result = backtest(weekly["net"], weekly["ending_cash"], cushion).mean()
        print(f"{name}  navie ={result['naive']:0.2f} "
            f"moving acerage= {result['moving_avg']:0.2f} "
            f"sesonal navie= {result['seasonal']:0.2f}")
        print(name, result[["seasonal_recall", "seasonal_precision"]].round(2).to_dict())

    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("baselines")

    results = {}
    with mlflow.start_run(run_name="baselines"):
        mlflow.log_param("folds", 4)
        mlflow.log_param("horizon", 13)
        for name in names:
            settings, df = load_file(f"data/synthetic/{name}.csv")
            weekly = weekly_table(df, float(settings["opening_cash_balance"]))
            cushion = float(settings["minimum_cash_cushion"])
            result = backtest(weekly["net"], weekly["ending_cash"], cushion).mean()
            results[name] = result
            for baseline in ["naive", "moving_avg", "seasonal"]:
                mlflow.log_metric(f"{name}_{baseline}_mae", result[baseline])    
        table = pd.DataFrame(results).T.round(2)
        table.to_csv("baseline_results.csv")
        mlflow.log_artifact("baseline_results.csv")
        pd.set_option("display.width", 200)
        pd.set_option("display.max_columns", 20)
        print(table)