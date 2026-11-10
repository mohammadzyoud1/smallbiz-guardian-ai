import sys

sys.path.insert(0, "backend")

import pandas as pd
from agent_tools import get_forecast, get_summary, run_scenario


def test_summary_reports_recent_averages():
    n = 12
    weekly = pd.DataFrame({
        "inflow": [1000.0] * n,
        "outflow": [800.0] * n,
        "net": [200.0] * n,
        "ending_cash": [5000.0 + 200 * (i + 1) for i in range(n)],
    })
    result = get_summary(weekly, cushion=3000)
    assert result["cash_now"] == 7400.0
    assert result["avg_weekly_net_12w"] == 200                


def test_forecast_returns_a_range_around_the_expected_cash():
    n = 60
    weekly = pd.DataFrame({
        "inflow": [1000.0] * n,
        "outflow": [800.0] * n,
        "net": [200.0] * n,
        "ending_cash": [5000.0 + 200 * (i + 1) for i in range(n)],
    })
    result = get_forecast(weekly, cushion=3000)
    assert result["cash_in_week_13_low"] <= result["cash_in_week_13"] <= result["cash_in_week_13_high"]
    assert result["weeks"] == 13                      


def test_run_scenario_reports_the_change():
    n = 60
    weekly = pd.DataFrame({
        "inflow": [1000.0] * n,
        "outflow": [800.0] * n,
        "net": [200.0] * n,
        "ending_cash": [5000.0 + 200 * (i + 1) for i in range(n)],
    })
    result = run_scenario(weekly, 3000, "cost_shock", amount=500, week=2)
    assert result["change_in_13_week_net"] == -500