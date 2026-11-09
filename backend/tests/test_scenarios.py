import sys

sys.path.insert(0, "backend")

import numpy as np
from server.scenarios import (
    break_even_lift,
    cost_shock_one_time,
    cost_shock_recurring,
    decision_lever,
    slow_season,
)


def test_slow_season_cuts_income_in_the_chosen_weeks():
    inflow = np.array([1000.0] * 13)
    outflow = np.array([800.0] * 13)
    new_in, new_out = slow_season(inflow, outflow, drop=0.20, start=3, length=2)
    assert new_in[2] == 800.0
    assert new_in[1] == 1000.0
    assert new_in[4] == 1000.0
    assert (new_out == 800.0).all()


def test_one_time_shock_changes_only_one_week():
    inflow = np.array([1000.0] * 13)
    outflow = np.array([800.0] * 13)
    _, new_out = cost_shock_one_time(inflow, outflow, amount=500, week=4)
    assert new_out[3] == 1300.0                              
    assert new_out[2] == 800.0
    assert new_out[4] == 800.0


def test_recurring_shock_raises_costs_from_the_start_week():
    inflow = np.array([1000.0] * 13)
    outflow = np.array([800.0] * 13)
    supplies = np.array([200.0] * 13)
    _, new_out = cost_shock_recurring(inflow, outflow, supplies, rate=0.10, week=5)
    assert new_out[3] == 800.0
    assert new_out[4] == 820.0
    assert new_out[12] == 820.0


def test_decision_lever_applies_price_and_demand_response():
    inflow = np.array([1000.0] * 13)
    outflow = np.array([800.0] * 13)
    new_in, new_out = decision_lever(inflow, outflow, price_change=0.10, demand_response=0.5, extra_cost=100, week=5)
    assert round(new_in[0], 2) == 1045.0                      
    assert new_out[3] == 800.0
    assert new_out[4] == 900.0


def test_break_even_lift():
    assert break_even_lift(np.array([1000.0] * 13), 150) == 0.15