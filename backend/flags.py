import numpy as np


def cushion_breach(forecast_net, cash_now, cushion):
    projected = cash_now + np.cumsum(np.array(forecast_net, dtype=float))
    below = projected < cushion
    if not below.any():
        return {"flag": False, "week": None, "amount": None,
                "reason": "Projected cash stays above your cushion for the next 13 weeks."}
    first = int(np.argmax(below)) + 1
    return {"flag": True, "week": first, "amount": float(projected[first - 1]),
            "reason": f"Cash is projected to fall below your cushion of {cushion:,.0f} in week {first}, to {projected[first - 1]:,.0f}."}


def runway(low_forecast_net, cash_now):
    projected = cash_now + np.cumsum(np.array(low_forecast_net, dtype=float))
    empty = projected <= 0                          
    if not empty.any():
        return {"flag": False, "weeks": "13+",
                "reason": "On the pessimistic forecast, your cash lasts the full 13 weeks."}
    weeks = int(np.argmax(empty)) + 1
    return {"flag": True, "weeks": weeks,
            "reason": f"On the pessimistic forecast, your cash runs out in week {weeks}."}

def expense_concentration(by_category, threshold=0.40, weeks=12):
    recent = by_category.tail(weeks)
    totals = recent.sum()
    share = totals / totals.sum()
    top = share.idxmax()
    if share[top] > threshold:                              
        return {"flag": True, "category": top, "share": float(share[top]),
                "reason": f"{top.capitalize()} is {share[top]:.0%} of your spending over the last {weeks} weeks."}
    return {"flag": False, "category": top, "share": float(share[top]),
            "reason": "No single category is more than 40% of your spending."}


def cost_creep(by_category, threshold=0.15):
    recent = by_category.tail(4).mean()
    earlier = by_category.iloc[-16:-12].mean()
    found = []
    for category in by_category.columns:
        if earlier[category] > 0:
            change = recent[category] / earlier[category] - 1
            if change > threshold:                              
                found.append((category, float(change)))
    if found:
        category, change = max(found, key=lambda item: item[1])
        return {"flag": True, "category": category, "change": change,
                "reason": f"{category.capitalize()} spending is up {change:.0%} compared with 12 weeks ago."}
    return {"flag": False, "category": None, "change": None,
            "reason": "No category has risen by more than 15% in the last 12 weeks."}

def revenue_volatility(inflow, threshold=0.35, weeks=12):
    recent = np.array(inflow.tail(weeks), dtype=float)
    mean = recent.mean()
    if mean <= 0:
        return {"flag": False, "cv": None, "reason": "There is not enough income in the last 12 weeks to measure."}
    cv = recent.std() / mean
    if cv > threshold:                                      # BLANK
        return {"flag": True, "cv": float(cv),
                "reason": f"Your weekly income has swung by about {cv:.0%} of its average over the last {weeks} weeks."}
    return {"flag": False, "cv": float(cv),
            "reason": "Your weekly income has been fairly steady over the last 12 weeks."}

def fixed_cost_coverage(inflow, by_category, threshold=0.75, weeks=12):
    income = np.array(inflow.tail(weeks), dtype=float)
    fixed = np.array(by_category.tail(weeks)[["rent", "payroll"]].sum(axis=1), dtype=float)
    covered = (income >= fixed).mean()
    if covered < threshold:                                 # BLANK
        return {"flag": True, "covered": float(covered),
                "reason": f"Your income covered rent and payroll in only {covered:.0%} of the last {weeks} weeks."}
    return {"flag": False, "covered": float(covered),
            "reason": f"Your income covered rent and payroll in {covered:.0%} of the last {weeks} weeks."}