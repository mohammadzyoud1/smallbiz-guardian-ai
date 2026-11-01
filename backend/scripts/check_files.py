import glob

import pandas as pd

ALLOWED_CATEGORIES = {
    "sales", "other_income", "rent", "payroll", "supplies", "inventory",
    "utilities", "loan_payment", "insurance", "marketing", "fees",
    "taxes", "equipment", "other",
}

for path in sorted(glob.glob("data/synthetic/*.csv")):
    settings = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                key, value = line[1:].strip().split("=", 1)
                settings[key.strip()] = value.strip()
    df = pd.read_csv(path, comment="#")

    problems = []
    if list(df.columns) != ["date", "type", "category", "amount", "note", "recurring"]:
        problems.append("wrong columns")
    if not set(df["type"]).issubset({"sale", "expense"}):
        problems.append("bad type values")
    if not set(df["category"]).issubset(ALLOWED_CATEGORIES):
        problems.append("unknown categories")
    if (df["amount"] <= 0).any():
        problems.append("non-positive amounts")
    if not set(df["recurring"]).issubset({"yes", "no"}):
        problems.append("bad recurring values")
    if df.duplicated().any():
        problems.append("duplicate rows")

    print(path, "|", len(df), "rows |", df["date"].min(), "to", df["date"].max(),
          "|", settings.get("opening_cash_balance"), "/", settings.get("minimum_cash_cushion"),
          "|", "OK" if not problems else problems)