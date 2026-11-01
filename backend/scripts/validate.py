import glob
import pandas as pd

ALLOWED = {
    "sales", "other_income", "rent", "payroll", "supplies", "inventory",
    "utilities", "loan_payment", "insurance", "marketing", "fees",
    "taxes", "equipment", "other",
}


def rows_text(mask):
    nums = [str(i + 1) for i in mask[mask].index[:5]]
    return ", ".join(nums) + (" ..." if mask.sum() > 5 else "")


def validate(path):
    errors, warnings, info = [], [], []

    # settings lines
    settings = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                key, _, value = line[1:].strip().partition("=")
                settings[key.strip()] = value.strip()
    if not settings.get("opening_cash_balance"):
        errors.append("The opening cash balance is missing from the settings.")

    # read everything as text so nothing can crash
    df = pd.read_csv(path, comment="#", dtype=str)
    missing_cols = [c for c in ["date", "type", "category", "amount"] if c not in df.columns]
    if missing_cols:
        errors.append("Missing columns: " + ", ".join(missing_cols))
        return errors, warnings, info

    dates = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    bad = dates.isna()
    if bad.any():
        errors.append(f"{bad.sum()} rows have a date that is not in YYYY-MM-DD format (rows: {rows_text(bad)}).")

    amounts = pd.to_numeric(df["amount"], errors="coerce")
    bad = amounts.isna()
    if bad.any():
        errors.append(f"{bad.sum()} rows have an amount that is not a number (rows: {rows_text(bad)}).")
    bad = amounts < 0
    if bad.any():
        errors.append(f"{bad.sum()} rows have a negative amount (rows: {rows_text(bad)}).")

    bad = ~df["type"].isin(["sale", "expense"])
    if bad.any():
        errors.append(f"{bad.sum()} rows have a type that is not sale or expense (rows: {rows_text(bad)}).")

    bad = ~df["category"].isin(ALLOWED)
    if bad.any():
        warnings.append(f"{bad.sum()} rows have an unknown category (rows: {rows_text(bad)}); they will be counted as 'other'.")

    dup = df.duplicated()
    if dup.any():
        warnings.append(f"{dup.sum()} rows are exact duplicates of another row (rows: {rows_text(dup)}).")
   
    good = dates.dropna()
    if len(good) > 0:
          middle = good.median()
          far = (good - middle).abs() > pd.Timedelta(days=1095)     
          if far.any():
              errors.append(f"{far.sum()} rows have a date more than 3 years from the rest of the data, which looks like a typo, such as 2052 instead of 2025 (rows: {rows_text(far.reindex(df.index, fill_value=False))}).")
              good = good[~far]
    if len(good) > 0:
        first, last = good.min(), good.max()
        weeks = (last - first).days / 7
        info.append(f"The data covers {first.date()} to {last.date()} ({weeks:.0f} weeks).")
        if weeks < 16:
            errors.append("There are fewer than 16 weeks of data, which is not enough to forecast.")
        elif weeks < 26:
            warnings.append("There are fewer than 26 weeks of data. A forecast is possible, but 26 or more is recommended.")
        have = set(good.dt.to_period("W"))
        missing = [w for w in pd.period_range(first, last, freq="W") if w not in have]
        if missing:
            warnings.append(f"{len(missing)} weeks have no transactions at all (the first is the week of {missing[0].start_time.date()}).")

    return errors, warnings, info

if __name__ == "__main__":
    for path in sorted(glob.glob("data/synthetic/*.csv") + glob.glob("data/messy/*.csv")):
        errors, warnings, info = validate(path)
        print(path, "->", "PASS" if not errors else "FAIL")
        for line in info:
            print("   info:   ", line)
        for line in warnings:
            print("   warning:", line)
        for line in errors:
            print("   ERROR:  ", line)