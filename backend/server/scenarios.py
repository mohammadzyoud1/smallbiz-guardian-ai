import numpy as np
from baselines import seasonal_naive


def baseline_table(weekly):
    inflow = seasonal_naive(weekly["inflow"])
    outflow = seasonal_naive(weekly["outflow"])
    return inflow, outflow


def summarize(inflow, outflow, cash_now, cushion):
    net = inflow - outflow
    cash = cash_now + np.cumsum(net)
    below = cash < cushion
    return {
        "lowest_cash": float(cash.min()),
        "lowest_week": int(cash.argmin()) + 1,
        "net_13_weeks": float(net.sum()),
        "breach_week": int(np.argmax(below)) + 1 if below.any() else None,
        "runway_weeks": int(np.argmax(cash <= 0)) + 1 if (cash <= 0).any() else "13+",
    }


def slow_season(inflow, outflow, drop, start, length):
    changed = np.array(inflow, dtype=float)
    first = start - 1
    last = min(start - 1 + length, 13)
    changed[first:last] = changed[first:last] * (1 - drop)         
    return changed, np.array(outflow, dtype=float)

def cost_shock_one_time(inflow, outflow, amount, week):
    changed = np.array(outflow, dtype=float)
    changed[week - 1] = changed[week - 1] + amount             
    return np.array(inflow, dtype=float), changed


def cost_shock_recurring(inflow, outflow, category_forecast, rate, week):
    changed = np.array(outflow, dtype=float)
    extra = np.array(category_forecast, dtype=float) * rate
    changed[week - 1:] = changed[week - 1:] + extra[week - 1:]
    return np.array(inflow, dtype=float), changed

def decision_lever(inflow, outflow, price_change, demand_response, extra_cost, week):
    new_inflow = np.array(inflow, dtype=float) * (1 + price_change) * (1 - demand_response * price_change)
    new_outflow = np.array(outflow, dtype=float)
    new_outflow[week - 1:] = new_outflow[week - 1:] + extra_cost             
    return new_inflow, new_outflow


def break_even_lift(inflow, extra_cost):
    average_income = float(np.mean(inflow))
    return extra_cost / average_income if average_income > 0 else None