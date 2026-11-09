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
    _good, problems = parse_file("data/messy/messy2.csv")
    assert len(problems) == 3                     


def test_weekly_net_is_inflow_minus_outflow():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-05", "2025-01-06", "2025-01-07", "2025-01-08", "2025-01-12", "2025-01-13"]),
        "type": ["sale", "sale", "sale", "expense", "sale", "sale"],
        "amount": [1.0, 100.0, 50.0, 30.0, 0.0, 1.0],
    })
    week = weekly_table(df, 1000.0)
    assert week["net"].iloc[0] == 120.0

def test_xlsx_template_is_parsed():
    good, problems = parse_file("data/templates/template_v1_example.xlsx")
    assert len(good) == 7 and len(problems) == 0


def test_category_columns_add_up_to_outflow():
    from ingest import load_file, weekly_by_category

    settings, df = load_file("data/synthetic/taqueria.csv")
    weekly = weekly_table(df, float(settings["opening_cash_balance"]))
    cats = weekly_by_category(df, weekly)
    assert abs(cats.sum(axis=1) - weekly["outflow"]).max() < 0.01