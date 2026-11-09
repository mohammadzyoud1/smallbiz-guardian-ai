import mlflow
import mlflow.pyfunc
import numpy as np
import pandas as pd
from band import collect_residuals
from ingest import load_file, weekly_table


class SeasonalForecaster(mlflow.pyfunc.PythonModel):
    def __init__(self, residuals):
        self.low_shift = float(np.percentile(residuals, 10))
        self.high_shift = float(np.percentile(residuals, 90))

    def predict(self, context, model_input):
        history = np.array(model_input["net"], dtype=float)
        season = 52 if len(history) >= 52 else 4
        forecast = np.array([history[len(history) - season + i % season] for i in range(13)])
        return pd.DataFrame({
            "low": forecast + self.low_shift,
            "forecast": forecast,
            "high": forecast + self.high_shift,
        })


if __name__ == "__main__":
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("forecaster")

    pooled = []
    for name in ["taqueria", "salon", "cleaning", "corner", "childcare", "tailor"]:
        settings, df = load_file(f"data/synthetic/{name}.csv")
        weekly = weekly_table(df, float(settings["opening_cash_balance"]))
        pooled.append(collect_residuals(weekly["net"]).flatten())
    residuals = np.concatenate(pooled)

    with mlflow.start_run(run_name="guardian-forecaster-v1"):
        mlflow.log_param("model", "seasonal_naive_with_band")
        mlflow.log_param("band_percentiles", "10-90")
        mlflow.log_param("reason", "global model beat the baseline on only 3 of 6")
        mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=SeasonalForecaster(residuals),
            registered_model_name="guardian-forecaster v1",             # BLANK
        )