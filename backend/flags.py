import numpy as np

# Standardized Message Helper

def message(code, **params):
    return {"code": code, "params": params}


# Cash Cushion Breach Detection
def cushion_breach(forecast_net, cash_now, cushion):

    # Calculate projected cash balances using the forecasted net cash flow
    projected = cash_now + np.cumsum(np.array(forecast_net, dtype=float))

    # Identify weeks when projected cash falls below the minimum cushion
    below = projected < cushion

    # Return a safe status if cash never falls below the required cushion
    if not below.any():
        return {"flag": False, "week": None, "amount": None,
                "reason": message("cushion_safe")}

    # Find the first week when projected cash falls below the cushion
    
    first = int(np.argmax(below)) + 1
    return {"flag": True, "week": first, "amount": float(projected[first - 1]),
            "reason": message(
    "cushion_breach",
    cushion=f"{cushion:,.0f}",
    week=first,
    amount=f"{projected[first - 1]:,.0f}"
)}


# Cash Runway Detection
def runway(low_forecast_net, cash_now):

    # Calculate projected cash balances using the lower forecast

    projected = cash_now + np.cumsum(np.array(low_forecast_net, dtype=float))

    # Identify weeks when projected cash reaches zero or becomes negative

    empty = projected <= 0                          
    if not empty.any():
        return {"flag": False, "weeks": "13+",
                "reason": message("runway_safe")}

    # Find the first week when the projected cash balance is depleted
    
    weeks = int(np.argmax(empty)) + 1
    return {"flag": True, "weeks": weeks,
            "reason": message("runway_breach", weeks=weeks)}


# Expense Concentration Detection
def expense_concentration(by_category, threshold=0.40, weeks=12):

    # Get expense data from the most recent specified number of weeks

    recent = by_category.tail(weeks)

    # Calculate the total expenses for each category

    totals = recent.sum()

    # Calculate each category's share of total expenses

    share = totals / totals.sum()

    # Identify the category with the largest expense share

    top = share.idxmax()

    # Check whether the largest category exceeds the concentration threshold

    if share[top] > threshold:  

        # Return a warning with the category and its percentage of expenses                            
        return {"flag": True, "category": top, "share": float(share[top]),
                "reason": message(
    "expense_concentration",
    category=top.capitalize(),
    share=f"{share[top]:.0%}",
    weeks=weeks
)}
    return {"flag": False, "category": top, "share": float(share[top]),
            "reason":  message("expense_concentration_safe")}


# Expense Cost Creep Detection

def cost_creep(by_category, threshold=0.15):

    # Calculate average expenses over the most recent four weeks

    recent = by_category.tail(4).mean()

    # Calculate average expenses from the four weeks before that

    earlier = by_category.iloc[-16:-12].mean()

    # Store categories where expenses have increased beyond the threshold

    found = []

    # Compare recent expenses against the earlier period for each category

    for category in by_category.columns:
        if earlier[category] > 0:

            # Calculate the percentage increase in the expense category            
            change = recent[category] / earlier[category] - 1

            # Record categories with an increase above the configured threshold

            if change > threshold:                              
                found.append((category, float(change)))
    # Return the category with the largest increase if any were found

    if found:

        # Select the category with the highest percentage increase

        category, change = max(found, key=lambda item: item[1])
        return {"flag": True, "category": category, "change": change,
                "reason": message(
    "cost_creep",
    category=category.capitalize(),
    change=f"{change:.0%}"
)}
    return {"flag": False, "category": None, "change": None,
            "reason": message("cost_creep_safe")}

# Revenue Volatility Detection
def revenue_volatility(inflow, threshold=0.35, weeks=12):

    # Extract recent revenue values as a NumPy array
    
    recent = np.array(inflow.tail(weeks), dtype=float)
    mean = recent.mean()

    # Avoid calculating volatility when average revenue is zero or negative
        
    if mean <= 0:
        return {"flag": False, "cv": None, "reason":  message("revenue_insufficient")}

    # Calculate the coefficient of variation (standard deviation / mean)     
    cv = recent.std() / mean
 

    # Check whether revenue volatility exceeds the configured threshold

    if cv > threshold:    

        # Return a warning when revenue fluctuates significantly                                
        return {"flag": True, "cv": float(cv),
                "reason": message(
    "revenue_volatile",
    cv=f"{cv:.0%}",
    weeks=weeks
)}
    return {"flag": False, "cv": float(cv),
            "reason": message("revenue_stable")}

# Fixed Cost Coverage Detection
def fixed_cost_coverage(inflow, by_category, threshold=0.75, weeks=12):

    # Extract recent weekly revenue values
    
    income = np.array(inflow.tail(weeks), dtype=float)

    # Calculate weekly fixed costs by combining rent and payroll

    fixed = np.array(by_category.tail(weeks)[["rent", "payroll"]].sum(axis=1), dtype=float)

    # Calculate the percentage of weeks where revenue covers fixed costs

    covered = (income >= fixed).mean()
    if covered < threshold:    
        
        # Return a warning when fixed cost coverage is insufficient
        
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