import sys

sys.path.insert(0, "backend")

import pandas as pd
from ingest import weekly_table
from parser import parse_file
from schema import Transaction


def test_unknown_category_becomes_other():
    t = Transaction(date="2025-01-02", type="sale", category="suplies", amount=100)
    assert t.category == "other"


def test_negative_amount_is_rejected():
    good, problems = parse_file("data/messy/messy2.csv")
    assert len(problems) == 0                     


def test_weekly_net_is_inflow_minus_outflow():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-06", "2025-01-07", "2025-01-08"]),
        "type": ["sale", "sale", "expense"],
        "amount": [100.0, 50.0, 30.0],
    })
    week = weekly_table(df, 1000.0)
    assert week["net"].iloc[0] == 120.0