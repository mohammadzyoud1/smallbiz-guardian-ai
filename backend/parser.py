import pandas as pd
from pydantic import ValidationError

from schema import Transaction


def parse_file(path):
    df = pd.read_csv(path, comment="#", dtype=str).fillna("")
    good, problems = [], []
    for i, row in df.iterrows():
        try:
            good.append(Transaction(**row.to_dict()))
        except ValidationError as error:
            fields = ", ".join(str(e["loc"][0]) for e in error.errors())
            problems.append(f"row {i + 1}: problem in {fields}")
    return good, problems


if __name__ == "__main__":
    for path in ["data/synthetic/taqueria.csv", "data/messy/messy2.csv"]:
        good, problems = parse_file(path)
        print(path, "->", len(good), "valid rows,", len(problems), "rejected")
        for line in problems[:10]:              
            print("  ", line," ",path)