import pandas as pd

path = "data/synthetic/taqueria.csv"

# Settings: the lines that start with "#"
settings = {}
with open(path, encoding="utf-8") as f:
    for line in f:
        if line.startswith("#"):
            key, value = line[1:].strip().split("=", 1)
            settings[key.strip()] = value.strip()

# Transactions: everything else (pandas skips the "#" lines)
df = pd.read_csv(path, comment="#")

print("SETTINGS:", settings)
print()
print(df)
print()
print(df.dtypes)