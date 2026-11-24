
import numpy as np
from band import make_band
from baselines import seasonal_naive
from flags import (
    cost_creep,
    cushion_breach,
    expense_concentration,
    fixed_cost_coverage,
    revenue_volatility,
    runway,
)
from server.scenarios import (
    baseline_table,
    break_even_lift,
    cost_shock_one_time,
    cost_shock_recurring,
    decision_lever,
    slow_season,
    summarize,
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

    # Extract the historical weekly net cash flow
    net = weekly["net"]

    # Generate the projected cash flow and its lower and upper ranges
    point, low, high = make_band(net, net)

    # Get the latest available ending cash balance
    cash_now = float(weekly["ending_cash"].iloc[-1])

    # Calculate projected cash balances over the forecast period
    cash = cash_now + np.cumsum(point)
    # Return the 13-week forecast and 
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

     # Generate projected net cash flow and its lower range
    point, low, _high = make_band(net, net)

    # Get the latest available cash balance
    cash_now = float(weekly["ending_cash"].iloc[-1])

    # Identify expense categories, excluding the main financial columns
    categories = [c for c in weekly.columns if c not in ("inflow", "outflow", "net", "ending_cash")]

    # Create a separate table containing expenses by category
    by_category = weekly[categories].copy()

    # Ensure rent and payroll columns exist for fixed-cost analysis
    for needed in ("rent", "payroll"):
        if needed not in by_category.columns:
            by_category[needed] = 0.0

    # Calculate and return the different financial risk indicators        
    return {
        "cushion_breach": cushion_breach(point, cash_now, cushion),
        "cushion_breach_worse_case": cushion_breach(low, cash_now, cushion),
        "runway": runway(low, cash_now),
        "expense_concentration": expense_concentration(by_category),
        "cost_creep": cost_creep(by_category),
        "revenue_volatility": revenue_volatility(weekly["inflow"]),
        "fixed_cost_coverage": fixed_cost_coverage(weekly["inflow"], by_category),
        "cushion": cushion,
    }


def run_scenario(weekly, cushion, name, **params):
    cash_now = float(weekly["ending_cash"].iloc[-1])

    # Build the baseline projected inflow and outflow
    inflow, outflow = baseline_table(weekly)

    # Calculate the financial results without any scenario changes
    base = summarize(inflow, outflow, cash_now, cushion)

    # Apply the selected scenario

    if name == "slow_season": # Simulate a period of reduced revenue
        new_in, new_out = slow_season(
            inflow, outflow, params.get("drop", 0.2), params.get("start", 1), params.get("length", 4))
    
    # Forecast expenses for a specific category       
    elif name == "cost_shock" and params.get("category"):
        forecast = seasonal_naive(weekly[params["category"]])

        # Apply a recurring increase to that expense category
        new_in, new_out = cost_shock_recurring(
            inflow, outflow, forecast, params.get("rate", 0.1), params.get("week", 1))

    # Apply a one-time unexpected expense        
    elif name == "cost_shock":
        new_in, new_out = cost_shock_one_time(inflow, outflow, params.get("amount", 1000), params.get("week", 1))

    # Simulate a business decision involving price, demand, and additional costs
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
    # For decision scenarios, also calculate the break-even sales lift
    if name == "decision_lever":
        result["break_even_lift"] = round(break_even_lift(inflow, params.get("extra_cost", 0)), 4)
    return result


def _clean(value):
    return round(value, 2) if isinstance(value, float) else value

# Compare Default Scenarios
def compare_scenarios(weekly, cushion):
    return {
        "slow_season": run_scenario(weekly, cushion, "slow_season", drop=0.2, start=1, length=4),
        "cost_shock": run_scenario(weekly, cushion, "cost_shock", amount=2000, week=1),
        "decision_lever": run_scenario(weekly, cushion, "decision_lever", price_change=0.05, demand_response=0.5, extra_cost=0, week=1),
    }