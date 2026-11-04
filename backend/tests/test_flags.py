import sys

sys.path.insert(0, "backend")
import numpy as pn
import pandas as pd
from flags import cushion_breach
from flags import runway
from flags import fixed_cost_coverage
from flags import expense_concentration
from flags import revenue_volatility
from flags import cost_creep
from flags import fixed_cost_coverage

def test_breach_is_found_in_the_right_week():
    result = cushion_breach([-500] * 13, cash_now=2000, cushion=1000)
    assert result["flag"] is True
    assert result["week"] == 3                    


def test_no_breach_when_cash_stays_high():
    result = cushion_breach([100] * 13, cash_now=5000, cushion=1000)
    assert result["flag"] is False




def test_runway_counts_weeks_until_cash_is_gone():
    result = runway([-400] * 13, cash_now=1000)
    assert result["weeks"] == 3                   


def test_runway_is_thirteen_plus_when_cash_lasts():
    result = runway([50] * 13, cash_now=500)
    assert result["weeks"] == "13+"






def test_concentration_flags_a_dominant_category():
    table = pd.DataFrame({"rent": [500] * 12, "supplies": [100] * 12, "payroll": [100] * 12})
    result = expense_concentration(table)
    assert result["flag"] is True
    assert result["category"] == "rent"                


def test_concentration_is_off_when_spread_evenly():
    table = pd.DataFrame({"rent": [100] * 12, "supplies": [100] * 12, "payroll": [100] * 12})
    result = expense_concentration(table)
    assert result["flag"] is False



def test_cost_creep_finds_a_rising_category():
    rows = [{"supplies": 100, "rent": 50}] * 12 + [{"supplies": 130, "rent": 50}] * 4
    result = cost_creep(pd.DataFrame(rows))
    assert result["flag"] is True
    assert result["category"] == "supplies"


def test_cost_creep_is_off_when_costs_are_flat():
    result = cost_creep(pd.DataFrame([{"supplies": 100, "rent": 50}] * 16))
    assert result["flag"] is False




def test_volatility_flags_wild_income():
    inflow = pd.Series([1000, 100, 1500, 50, 2000, 100, 1800, 200, 1200, 100, 1600, 150])
    result = revenue_volatility(inflow)
    assert result["flag"] is True                       


def test_volatility_is_off_for_steady_income():
    inflow = pd.Series([1000, 1010, 990, 1005, 995, 1000, 1010, 990, 1000, 1005, 995, 1000])
    result = revenue_volatility(inflow)
    assert result["flag"] is False


def test_coverage_flags_when_income_often_falls_short():
    inflow = pd.Series([500] * 12)
    costs = pd.DataFrame({"rent": [600] * 6 + [100] * 6, "payroll": [0] * 12})
    result = fixed_cost_coverage(inflow, costs)
    assert result["covered"] == ____                   # BLANK


def test_coverage_is_fine_when_income_is_high():
    inflow = pd.Series([2000] * 12)
    costs = pd.DataFrame({"rent": [600] * 12, "payroll": [500] * 12})
    result = fixed_cost_coverage(inflow, costs)
    assert result["flag"] is False


def test_coverage_flags_when_income_often_falls_short():
    inflow = pd.Series([500] * 12)
    costs = pd.DataFrame({"rent": [600] * 6 + [100] * 6, "payroll": [0] * 12})
    result = fixed_cost_coverage(inflow, costs)
    assert result["covered"] == 0.5                  


def test_coverage_is_fine_when_income_is_high():
    inflow = pd.Series([2000] * 12)
    costs = pd.DataFrame({"rent": [600] * 12, "payroll": [500] * 12})
    result = fixed_cost_coverage(inflow, costs)
    assert result["flag"] is False