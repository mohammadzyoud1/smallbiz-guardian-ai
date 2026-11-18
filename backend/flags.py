import numpy as np
def message(code, **params):
    return {"code": code, "params": params}

def cushion_breach(forecast_net, cash_now, cushion):
    projected = cash_now + np.cumsum(np.array(forecast_net, dtype=float))
    below = projected < cushion
    if not below.any():
        return {"flag": False, "week": None, "amount": None,
                "reason": message("cushion_safe")}
    first = int(np.argmax(below)) + 1
    return {"flag": True, "week": first, "amount": float(projected[first - 1]),
            "reason": message(
    "cushion_breach",
    cushion=f"{cushion:,.0f}",
    week=first,
    amount=f"{projected[first - 1]:,.0f}"
)}


def runway(low_forecast_net, cash_now):
    projected = cash_now + np.cumsum(np.array(low_forecast_net, dtype=float))
    empty = projected <= 0                          
    if not empty.any():
        return {"flag": False, "weeks": "13+",
                "reason": message("runway_safe")}
    weeks = int(np.argmax(empty)) + 1
    return {"flag": True, "weeks": weeks,
            "reason": message("runway_breach", weeks=weeks)}

def expense_concentration(by_category, threshold=0.40, weeks=12):
    recent = by_category.tail(weeks)
    totals = recent.sum()
    share = totals / totals.sum()
    top = share.idxmax()
    if share[top] > threshold:                              
        return {"flag": True, "category": top, "share": float(share[top]),
                "reason": message(
    "expense_concentration",
    category=top.capitalize(),
    share=f"{share[top]:.0%}",
    weeks=weeks
)}
    return {"flag": False, "category": top, "share": float(share[top]),
            "reason":  message("expense_concentration_safe")}


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
                "reason": message(
    "cost_creep",
    category=category.capitalize(),
    change=f"{change:.0%}"
)}
    return {"flag": False, "category": None, "change": None,
            "reason": message("cost_creep_safe")}

def revenue_volatility(inflow, threshold=0.35, weeks=12):
    recent = np.array(inflow.tail(weeks), dtype=float)
    mean = recent.mean()
    if mean <= 0:
        return {"flag": False, "cv": None, "reason":  message("revenue_insufficient")}
    cv = recent.std() / mean
    if cv > threshold:                                    
        return {"flag": True, "cv": float(cv),
                "reason": message(
    "revenue_volatile",
    cv=f"{cv:.0%}",
    weeks=weeks
)}
    return {"flag": False, "cv": float(cv),
            "reason": message("revenue_stable")}

def fixed_cost_coverage(inflow, by_category, threshold=0.75, weeks=12):
    income = np.array(inflow.tail(weeks), dtype=float)
    fixed = np.array(by_category.tail(weeks)[["rent", "payroll"]].sum(axis=1), dtype=float)
    covered = (income >= fixed).mean()
    if covered < threshold:                                 
        return {"flag": True, "covered": float(covered),
                "reason": message(
    "fixed_cost_low",
    covered=f"{covered:.0%}",
    weeks=weeks
)}
    return {"flag": False, "covered": float(covered),
            "reason": message(
    "fixed_cost_good",
    covered=f"{covered:.0%}",
    weeks=weeks
)}