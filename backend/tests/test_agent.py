import sys

sys.path.insert(0, "backend")
sys.path.insert(0, "backend/llm")

import pandas as pd
from agent import ask
from faithfulness import check_answer
from llm.llm_provider import FakeProvider


def make_weekly():
    n = 60
    return pd.DataFrame({
        "inflow": [1000.0] * n, "outflow": [800.0] * n, "net": [200.0] * n,
        "ending_cash": [5000.0 + 200 * (i + 1) for i in range(n)],
    })


def test_agent_uses_a_tool_then_answers():
    provider = FakeProvider([
        {"tool_calls": [{"id": "1", "name": "get_summary", "arguments": {}}]},
        {"text": "Your cash is 17,000 and your cushion is 3,000."},
    ])
    result = ask(provider, "How am I doing?", make_weekly(), 3000.0)
    assert len(result["tool_outputs"]) == 1
    assert check_answer(result["answer"], result["tool_outputs"])["faithful"] is True