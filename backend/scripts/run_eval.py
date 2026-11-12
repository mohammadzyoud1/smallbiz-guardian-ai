import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "llm"))

from agent import ask
from dotenv import load_dotenv
from eval_set import QUESTIONS
from faithfulness import check_answer
from ingest import load_file, weekly_by_category, weekly_table
from llm_provider import GroqProvider


def load_business(name):
    settings, df = load_file(f"data/synthetic/{name}.csv")
    weekly = weekly_table(df, float(settings["opening_cash_balance"]))
    weekly = weekly.join(weekly_by_category(df, weekly))
    return weekly, float(settings["minimum_cash_cushion"])


if __name__ == "__main__":
    load_dotenv()
    provider = GroqProvider()
    passed = total_tokens = 0
    for item in QUESTIONS:
        weekly, cushion = load_business(item["business"])
        result = ask(provider, item["question"], weekly, cushion)
        faithful = check_answer(result["answer"], result["tool_outputs"])["faithful"]
        plain = result["answer"].replace("*", "").replace("\u00a0", " ").lower()
        covered = all(text.lower() in plain for text in item["must_mention"])
        ok = faithful and covered
        passed += ok
        total_tokens += result["tokens"]
        print(f"{'PASS' if ok else 'FAIL'}  {item['business']:<9} {item['question']}  (faithful={faithful}, covered={covered})")
        if not ok:
            print("   unsupported:", check_answer(result["answer"], result["tool_outputs"])["unsupported_numbers"])
            print("   answer:", result["answer"].replace("\n", " "))
    print(f"\n{passed}/{len(QUESTIONS)} passed | tokens: {total_tokens}")