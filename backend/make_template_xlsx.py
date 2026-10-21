import pandas as pd

csv_path = "data/templates/template_v1_example.csv"
xlsx_path = "data/templates/template_v1_example.xlsx"

# Read the CSV the same way as before
settings = {}
with open(csv_path, encoding="utf-8") as f:
    for line in f:
        if line.startswith("#"):
            key, value = line[1:].strip().split("=", 1)
            settings[key.strip()] = value.strip()

transactions = pd.read_csv(csv_path, comment="#")

settings_df = pd.DataFrame(
    {"field": list(settings.keys()), "value": list(settings.values())}
)

# Write two sheets
with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
    transactions.to_excel(writer, sheet_name="transactions", index=False)
    settings_df.to_excel(writer, sheet_name="settings", index=False)

print("Created", xlsx_path)