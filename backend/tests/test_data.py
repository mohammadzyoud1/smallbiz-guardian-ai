import os

import pandas as pd

CLEAN = ["taqueria", "salon", "cleaning", "corner", "childcare", "tailor"]
COLUMNS = ["date", "type", "category", "amount", "note", "recurring"]


def load(name):
    return pd.read_csv(f"data/synthetic/{name}.csv", comment="#")


def test_pytest_runs():
    assert 1 + 1 == 2


def test_six_clean_files_exist():
    for name in CLEAN:
        assert os.path.exists(f"data/synthetic/{name}.csv"), name


def test_columns_match_template():
    for name in CLEAN:
        assert list(load(name).columns) == COLUMNS, name


def test_amounts_are_positive_numbers():
    for name in CLEAN:
        assert (load(name)["amount"] > 0).all(), name


def test_types_are_sale_or_expense():
    for name in CLEAN:
        assert set(load(name)["type"]) <= {"sale", "expense"}, name



def test_messy_file_has_a_bad_amount():
    df = pd.read_csv("data/messy/messy.csv", comment="#", dtype=str)
    amounts = pd.to_numeric(df["amount"], errors="coerce")
    assert amounts.isna().any() or (amounts < 0).any()