
import numpy as np

from band import make_band
from flags import (
    cost_creep, cushion_breach, expense_concentration,
    fixed_cost_coverage, revenue_volatility, runway,
)
from baselines import seasonal_naive
from server.scenarios import (
    baseline_table, break_even_lift, cost_shock_one_time,
    cost_shock_recurring, decision_lever, slow_season, summarize,
)

def get_summary(weekly, cushion):
    last12 = weekly.tail(12)
    return {
        "weeks_of_data": len(weekly),
        "cash_now": round(float(weekly["ending_cash"].iloc[-1]), 2),
        "cushion": cushion,
        "avg_weekly_inflow_12w": round(float(last12["inflow"].mean()), 2),
        "avg_weekly_outflow_12w": round(float(last12["outflow"].mean()), 2),
        "avg_weekly_net_12w": round(float(last12["net"].mean()), 2),
    }


def get_forecast(weekly, cushion):
    net = weekly["net"]
    point, low, high = make_band(net, net)
    cash_now = float(weekly["ending_cash"].iloc[-1])
    cash = cash_now + np.cumsum(point)
    return {
        "weeks": 13,
        "lowest_projected_cash": round(float(cash.min()), 2),
        "lowest_projected_cash_week": int(cash.argmin()) + 1,
        "cash_in_week_13": round(float(cash[-1]), 2),
        "cash_in_week_13_low": round(float((cash_now + np.cumsum(low))[-1]), 2),
        "cash_in_week_13_high": round(float((cash_now + np.cumsum(high))[-1]), 2),  
        "cushion": cushion,
    }


def get_flags(weekly, cushion):
    net = weekly["net"]
    point, low, _high = make_band(net, net)
    cash_now = float(weekly["ending_cash"].iloc[-1])
    categories = [c for c in weekly.columns if c not in ("inflow", "outflow", "net", "ending_cash")]
    by_category = weekly[categories].copy()
    for needed in ("rent", "payroll"):
        if needed not in by_category.columns:
            by_category[needed] = 0.0
    return {
        "cushion_breach": cushion_breach(point, cash_now, cushion),
        "cushion_breach_worse_case": cushion_breach(low, cash_now, cushion),
        "runway": runway(low, cash_now),
        "expense_concentration": expense_concentration(by_category),
        "cost_creep": cost_creep(by_category),
        "revenue_volatility": revenue_volatility(weekly["inflow"]),
        "fixed_cost_coverage": fixed_cost_coverage(weekly["inflow"], by_category),
    }


def run_scenario(weekly, cushion, name, **params):
    cash_now = float(weekly["ending_cash"].iloc[-1])
    inflow, outflow = baseline_table(weekly)
    base = summarize(inflow, outflow, cash_now, cushion)

    if name == "slow_season":
        new_in, new_out = slow_season(
            inflow, outflow, params.get("drop", 0.2), params.get("start", 1), params.get("length", 4))
    elif name == "cost_shock" and params.get("category"):
        forecast = seasonal_naive(weekly[params["category"]])
        new_in, new_out = cost_shock_recurring(
            inflow, outflow, forecast, params.get("rate", 0.1), params.get("week", 1))
    elif name == "cost_shock":
        new_in, new_out = cost_shock_one_time(inflow, outflow, params.get("amount", 1000), params.get("week", 1))
    elif name == "decision_lever":
        new_in, new_out = decision_lever(
            inflow, outflow, params.get("price_change", 0), params.get("demand_response", 0),
            params.get("extra_cost", 0), params.get("week", 1))
    else:
        return {"error": "Unknown scenario."}

    changed = summarize(new_in, new_out, cash_now, cushion)                  
    result = {
        "scenario": name,
        "baseline": {k: _clean(v) for k, v in base.items()},
        "with_scenario": {k: _clean(v) for k, v in changed.items()},
        "change_in_13_week_net": round(changed["net_13_weeks"] - base["net_13_weeks"], 2),
        "change_in_lowest_cash": round(changed["lowest_cash"] - base["lowest_cash"], 2),
    }
    if name == "decision_lever":
        result["break_even_lift"] = round(break_even_lift(inflow, params.get("extra_cost", 0)), 4)
    return result


def _clean(value):
    return round(value, 2) if isinstance(value, float) else value


def compare_scenarios(weekly, cushion):
    return {
        "slow_season": run_scenario(weekly, cushion, "slow_season", drop=0.2, start=1, length=4),
        "cost_shock": run_scenario(weekly, cushion, "cost_shock", amount=2000, week=1),
        "decision_lever": run_scenario(weekly, cushion, "decision_lever",
                                       price_change=0.05, demand_response=0.5, extra_cost=0, week=1),
    }