import json

from agent_prompt import SYSTEM_PROMPT
from agent_tools import (
    compare_scenarios,
    get_flags,
    get_forecast,
    get_summary,
    run_scenario,
)

TOOL_SPECS = [
    {"type": "function", "function": {
        "name": "get_summary", "description": "Current cash, cushion and 12-week averages for the business.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "get_forecast", "description": "13-week cash forecast: lowest cash and week, and cash in week 13 with a low and high range.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "get_flags", "description": "The vulnerability flags: cushion breach, runway, expense concentration, cost creep, revenue volatility, fixed-cost coverage.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "run_scenario", "description": "Run one what-if scenario on the forecast.",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string", "enum": ["slow_season", "cost_shock", "decision_lever"]},
            "drop": {"type": "number"}, "start": {"type": "integer"}, "length": {"type": "integer"},
            "amount": {"type": "number"}, "week": {"type": "integer"},
            "category": {"type": "string"}, "rate": {"type": "number"},
            "price_change": {"type": "number"}, "demand_response": {"type": "number"},
            "extra_cost": {"type": "number"}},
            "required": ["name"]}}},
    {"type": "function", "function": {
        "name": "compare_scenarios", "description": "Compare the three scenarios with moderate default values.",
        "parameters": {"type": "object", "properties": {}}}},
]


def run_tool(name, arguments, weekly, cushion):
    if name == "get_summary":
        return get_summary(weekly, cushion)
    if name == "get_forecast":
        return get_forecast(weekly, cushion)
    if name == "get_flags":
        return get_flags(weekly, cushion)
    if name == "run_scenario":
        return run_scenario(weekly, cushion, **arguments)
    if name == "compare_scenarios":
        return compare_scenarios(weekly, cushion)
    return {"error": "Unknown tool."}


def ask(provider, question, weekly, cushion, max_rounds=4):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    tool_outputs, tokens = [], 0
    for _ in range(max_rounds):
        reply = provider.chat(messages, TOOL_SPECS)
        tokens += reply["tokens"]
        if not reply["tool_calls"]:
            return {"answer": reply["text"], "tool_outputs": tool_outputs, "tokens": tokens}
        messages.append({
            "role": "assistant", "content": reply["text"],
            "tool_calls": [
                {"id": c["id"], "type": "function",
                 "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}}
                for c in reply["tool_calls"]],
        })
        for call in reply["tool_calls"]:
            result = run_tool(call["name"], call["arguments"], weekly, cushion)
            tool_outputs.append(result)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})  
    return {"answer": "I could not finish that question. Please try asking it differently.",
            "tool_outputs": tool_outputs, "tokens": tokens}