import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "llm"))

from agent import ask
from dotenv import load_dotenv
from faithfulness import check_answer
from faithfulness import numbers_in
from ingest import load_file, weekly_by_category, weekly_table
from llm_provider import GroqProvider

load_dotenv()
settings, df = load_file("data/synthetic/corner.csv")
weekly = weekly_table(df, float(settings["opening_cash_balance"]))
weekly = weekly.join(weekly_by_category(df, weekly))
cushion = float(settings["minimum_cash_cushion"])

result = ask(GroqProvider(), "Will I run low on cash, and what should I look at first?", weekly, cushion)
print(result["answer"])
print()
print("tools used:", len(result["tool_outputs"]), "| tokens:", result["tokens"])
print(check_answer(result["answer"], result["tool_outputs"]))
print(numbers_in("13‑week net of $1,399.21 and 3 practical options"))