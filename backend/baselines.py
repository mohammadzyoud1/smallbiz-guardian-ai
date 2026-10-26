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

#test the simple forcast 
def backtest(net, folds=4, horizon=13):
    rows = []
    for k in range(folds):
        end = len(net) - (k * horizon)                  
        history = net.iloc[:(end - horizon)]                     
        actual = net.iloc[end - horizon:end]
        rows.append({
            "naive": mae(actual, naive(history)),
            "moving_avg": mae(actual, moving_average(history)),
            "seasonal": mae(actual, seasonal_naive(history)),
        })
    return pd.DataFrame(rows)

names = ["taqueria", "salon", "cleaning", "corner", "childcare", "tailor"]
for name in names:
    settings, df = load_file(f"data/synthetic/{name}.csv")
    weekly = weekly_table(df, float(settings["opening_cash_balance"]))
    result = backtest(weekly["net"]).mean()
    print(f"{name}  navie ={result['naive']:0.2f} "
          f"moving acerage= {result['moving_avg']:0.2f} "
          f"sesonal navie= {result['seasonal']:0.2f}")

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("baselines")

results = {}
with mlflow.start_run(run_name="baselines"):
    mlflow.log_param("folds", 4)
    mlflow.log_param("horizon", 13)
    for name in names:
        settings, df = load_file(f"data/synthetic/{name}.csv")
        weekly = weekly_table(df, float(settings["opening_cash_balance"]))
        result = backtest(weekly["net"]).mean()
        results[name] = result
        for baseline in ["naive", "moving_avg", "seasonal"]:
            mlflow.log_metric(f"{name}_{baseline}_mae", result[baseline])    
    table = pd.DataFrame(results).T.round(0)
    table.to_csv("baseline_results.csv")
    mlflow.log_artifact("baseline_results.csv")
    print(table)