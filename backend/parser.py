import pandas as pd
from pydantic import ValidationError
from schema import Transaction


# 1. Parse and Validate an Uploaded File
def parse_file(path):
    settings={}
    
    #Read an Excel File
    if str(path).endswith(".xlsx"):
        # Read transaction records from the "transactions" worksheet. Read all values as strings and replace missing cells with empty strings.
        df = pd.read_excel(path, sheet_name="transactions", dtype=str).fillna("")
        df["date"] = df["date"].str[:10] 
        # Read business settings from the "settings" worksheet.         
        settings_df = pd.read_excel(path, sheet_name="settings", dtype=str).fillna("")

        # Convert the settings worksheet into a dictionary.
        settings = dict(zip(
            settings_df["key"].str.strip(),
            settings_df["value"].str.strip()
        ))
    # Read a CSV File        
    else:
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                # Lines beginning with "#" contain business settings.
                if line.startswith("#"):
                    # Split each setting into its key and value using "=" and store them.
                    key, _, value = line[1:].strip().partition("=")
                    settings[key.strip()] = value.strip()
        df = pd.read_csv(path, comment="#", dtype=str).fillna("")

    # Validate Transaction Records        
    good, problems = [], []
    for i, row in df.iterrows():
        try:
            good.append(Transaction(**row.to_dict()))
        except ValidationError as error:
            fields = ", ".join(str(e["loc"][0]) for e in error.errors())
            problems.append(f"row {i + 1}: problem in {fields}")
    return good, problems, settings, df


if __name__ == "__main__":
    for path in ["data/synthetic/taqueria.csv", "data/messy/messy2.csv"]:
        good, problems, settings, df = parse_file(path)
        print(path, "->", len(good), "valid rows,", len(problems), "rejected")
        for line in problems[:10]:              
            print("  ", line," ",path)