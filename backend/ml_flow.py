import glob
import os
import mlflow
import pandas as pd

mlflow.set_experiment("synthetic-data")

with mlflow.start_run(run_name="week1-generator"):
    mlflow.log_param("seed", 42)                  # BLANK: the seed from make_synthetic.py
    files = sorted(glob.glob("data/synthetic/*.csv"))
    mlflow.log_param("businesses", len(files))
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        df = pd.read_csv(path, comment="#")
        mlflow.log_metric(f"rows_{name}", len(df))
    print("Logged", len(files), "businesses")