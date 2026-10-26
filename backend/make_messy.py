import os
import pandas as pd

src = "data/synthetic/salon.csv"
with open(src, encoding="utf-8") as f:
    settings = [line for line in f if line.startswith("#")]
df = pd.read_csv(src, comment="#")

# 1. missing weeks: remove two full weeks (Mon May 5 to Sun May 18, 2025)
dates = pd.to_datetime(df["date"])
df = df[~((dates >= "2025-05-05") & (dates <= "2025-05-18"))].reset_index(drop=True)

# 2. a 2025 date typed as 2052
df.loc[150, "date"] = df.loc[150, "date"].replace("2025", "2052")

# 3. duplicated rows: copy 5 random rows and add them at the end
copies = df.sample(5, random_state=1)
df = pd.concat([df, copies], ignore_index=True)

os.makedirs("data/messy", exist_ok=True)
with open("data/messy/messy_2.csv", "w", encoding="utf-8", newline="") as f:
    f.writelines(settings)
    df.to_csv(f, index=False)

print("Saved data/messy/messy.csv", len(df), "rows")
print(df.loc[[150]])