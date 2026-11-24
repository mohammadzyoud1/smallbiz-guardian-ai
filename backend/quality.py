import pandas as pd
from parser import parse_file
from scripts.validate import ALLOWED, rows_text


# 1. Standardized Message Structure
def message(code, **params):
    return {
        "code": code,
        "params": params
    }

#  Validate Uploaded Transaction Data
def validate(path):
    errors, warnings, info = [], [], []
    settings = {}
    # read everything as text so nothing can crash
    good, problems, settings, df = parse_file(path)
    if not settings.get("opening_cash_balance"):
        errors.append(message("missing_opening_cash"))

    # Include transaction-level validation problems from the parser.
    if problems:
        errors.extend(
            message("invalid_transaction", details=problem)
            for problem in problems
        )
    # Check whether all required transaction columns exist.
    missing_cols = [c for c in ["date", "type", "category", "amount"] if c not in df.columns]
    if missing_cols:
        errors.append(message(
        "missing_columns",
        columns=", ".join(missing_cols)
    ))
        return errors, warnings, info

    #  Validate Dates and Amounts
    # Convert dates using a strict format.

    dates = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    bad = dates.isna()
    if bad.any():
        errors.append(message(
        "invalid_date_format",
        count=int(bad.sum()),
        rows=rows_text(bad)
    ))
    # Convert amounts to numbers; invalid values become NaN.
    amounts = pd.to_numeric(df["amount"], errors="coerce")

    
    bad = amounts.isna()
    if bad.any():
        errors.append(message(
            "invalid_amount",
            count=int(bad.sum()),
            rows=rows_text(bad)
        ))
    # Reject negative transaction amounts.
    bad = amounts < 0
    if bad.any():
        errors.append(message(
            "negative_amount",
            count=int(bad.sum()),
            rows=rows_text(bad)
        ))
    # Validate Transaction Types and Categories

    # Only sales and expenses are accepted transaction types.
    bad = ~df["type"].isin(["sale", "expense"])
    if bad.any():
        errors.append(message(
            "invalid_transaction_type",
            count=int(bad.sum()),
            rows=rows_text(bad)
        ))
    # Unknown categories generate warnings rather than errors.
    bad = ~df["category"].isin(ALLOWED)
    if bad.any():
        warnings.append(message(
            "unknown_category",
            count=int(bad.sum()),
            rows=rows_text(bad)
        ))
    # Detect rows that are exact duplicates across all columns.
    dup = df.duplicated()
    if dup.any():
        warnings.append(message(
            "duplicate_rows",
            count=int(dup.sum()),
            rows=rows_text(dup)
        ))
    # Check Date Range and Historical Coverage
    good = dates.dropna()
    if len(good) > 0:
          middle = good.median()

          # Flag dates more than three years (1095 days) away  from the median date as potential outliers.
          far = (good - middle).abs() > pd.Timedelta(days=1095)     
          if far.any():
              errors.append(message(
                "dates_far_from_median",
                count=int(far.sum()),
                rows=rows_text(
                    far.reindex(df.index, fill_value=False)
                )
            ))
              good = good[~far]
    if len(good) > 0:
        first, last = good.min(), good.max()
        # Calculate the approximate number of weeks between the first and last valid transaction dates.
        weeks = (last - first).days / 7
        info.append(message(
            "data_coverage",
            first=first.date().isoformat(),
            last=last.date().isoformat(),
            weeks=round(weeks)
        ))

         # Require at least 16 weeks of history. Recommend 26 weeks for more reliable forecasting.
        if weeks < 16:
            errors.append(message(
                "insufficient_history",
                minimum=16
            ))
        elif weeks < 26:
            warnings.append(message(
                "short_history",
                recommended=26
            ))

        # Convert transaction dates into weekly periods.
        have = set(good.dt.to_period("W"))
        missing = [w for w in pd.period_range(first, last, freq="W") if w not in have]
        if missing:
            warnings.append(message(
                "weeks_without_transactions",
                count=len(missing),
                first_week=missing[0].start_time.date().isoformat()
            ))

    return errors, warnings, info

#  Generate the Overall Quality Report
def quality_report(path):
    errors, warnings, info = validate(path)
    weeks = None

    # Retrieve the historical coverage value from the structured information messages.
    for line in info:
        if "weeks" in line:
            weeks = int(line.split("(")[1].split(" ")[0])

    # Determine whether the uploaded dataset is ready for forecasting.
    verdict = message("unknown")
    if weeks is not None:
        if weeks < 16:
            verdict = message(
                "not_enough_history",
                minimum=16
            )
        elif weeks < 26:
            verdict = message(
                "forecast_recommended",
                recommended=26
            )
        elif len(errors)>0:
            verdict=message("fix_errors_first")
        else:
            verdict = message("enough_history")
    return {
        "file": path,
        "passed": len(errors) == 0,           
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "forecast_ready": verdict,
    }

def format_message(item):
    code = item["code"]
    params = item.get("params", {})

    if not params:
        return code

    details = ", ".join(
        f"{key}={value}"
        for key, value in params.items()
    )

    return f"{code} ({details})"
def report_text(report):
    lines = [
        f"File: {report['file']}",
        "Result: " + ("PASS" if report["passed"] else "FAIL"),
        "Forecast: " + format_message(report["forecast_ready"])
    ]
    for label, items in [("Info", report["info"]), ("Warnings", report["warnings"]), ("Errors", report["errors"])]:
        if items:
            lines.append(label + ":")
            lines.extend(
                "  - " + format_message(item)
                for item in items
            )
    return "\n".join(lines) 
if __name__ == "__main__":
    import glob

    for path in sorted(glob.glob("data/synthetic/*.csv") + glob.glob("data/messy/*.csv")):
        report = quality_report(path)
        status = "PASS" if report["passed"] else "FAIL"
   
        print(f"{status}  {path}  ({len(report['errors'])} errors, {len(report['warnings'])} warnings)")

    print()
    print(report_text(quality_report("data/messy/messy2.csv")))

