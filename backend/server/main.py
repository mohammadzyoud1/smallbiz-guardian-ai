import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Literal

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from band import make_band
from baselines import seasonal_naive
from fastapi import FastAPI, File, HTTPException, UploadFile
from flags import (
    cost_creep,
    cushion_breach,
    expense_concentration,
    fixed_cost_coverage,
    revenue_volatility,
    runway,
)
from agent import ask as run_agent
from faithfulness import check_answer
from llm.llm_provider import GroqProvider
from rec_log import feedback_counts, log_exchange, set_feedback
from ingest import load_file, weekly_by_category, weekly_table
from pydantic import BaseModel
from quality import quality_report
from scenarios import (
    baseline_table,
    break_even_lift,
    cost_shock_one_time,
    cost_shock_recurring,
    decision_lever,
    slow_season,
    summarize,
)

DISCLAIMER = (
    "SmallBiz Guardian AI is an educational planning tool. "
    "It is not financial, legal, or tax advice."
)
SESSION_SECONDS = 60 * 60

app = FastAPI(title="SmallBiz Guardian AI")
sessions = {}


def clean_sessions():
    now = time.time()
    for key in [k for k, v in sessions.items() if now - v["created"] > SESSION_SECONDS]:
        del sessions[key]


@app.get("/health")
def health():
    return {"status": "ok", "disclaimer": DISCLAIMER}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    clean_sessions()
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    report = quality_report(path)
    if not report["passed"]:
        Path(path).unlink(missing_ok=True)
        return {"session_id": None, "report": report}

    settings, df = load_file(path)
    weekly = weekly_table(df, float(settings["opening_cash_balance"]))
    weekly = weekly.join(weekly_by_category(df, weekly))
    Path(path).unlink(missing_ok=True)

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "created": time.time(),
        "weekly": weekly,
        "cushion": float(settings.get("minimum_cash_cushion", 0)),
    }
    return {"session_id": session_id, "weeks": len(weekly), "report": report}


def get_session(session_id: str):
    clean_sessions()
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired.")    # BLANK
    return sessions[session_id]

@app.get("/forecast")
def forecast(session_id: str):
    s = get_session(session_id)
    weekly = s["weekly"]
    net = weekly["net"]
    point, low, high = make_band(net, net)
    cash_now = float(weekly["ending_cash"].iloc[-1])
    return {
        "weeks": list(range(1, 14)),
        "net": {
            "low": [round(float(x), 2) for x in low],
            "forecast": [round(float(x), 2) for x in point],
            "high": [round(float(x), 2) for x in high],
        },
        "ending_cash": {
            "low": [round(float(x), 2) for x in cash_now + np.cumsum(low)],      
            "forecast": [round(float(x), 2) for x in cash_now + np.cumsum(point)],
            "high": [round(float(x), 2) for x in cash_now + np.cumsum(high)],
        },
        "cushion": s["cushion"],
        "disclaimer": DISCLAIMER,
    }

@app.get("/flags")
def flags(session_id: str):
    s = get_session(session_id)
    weekly = s["weekly"]
    net = weekly["net"]
    point, low, _high = make_band(net, net)
    cash_now = float(weekly["ending_cash"].iloc[-1])

    categories = [c for c in weekly.columns if c not in ("inflow", "outflow", "net", "ending_cash")]
    by_category = weekly[categories].copy()
    for needed in ("rent", "payroll"):
        if needed not in by_category.columns:
            by_category[needed] = 0.0

    return {
        "cushion_breach": cushion_breach(point, cash_now, s["cushion"]),
        "cushion_breach_worse_case": cushion_breach(low, cash_now, s["cushion"]),
        "runway": runway(low, cash_now),                                   
        "expense_concentration": expense_concentration(by_category),
        "cost_creep": cost_creep(by_category),
        "revenue_volatility": revenue_volatility(weekly["inflow"]),
        "fixed_cost_coverage": fixed_cost_coverage(weekly["inflow"], by_category),
        "disclaimer": DISCLAIMER,
    }


class ScenarioRequest(BaseModel):
    session_id: str
    name: Literal["slow_season", "cost_shock", "decision_lever"]
    drop: float = 0.2
    start: int = 1
    length: int = 4
    amount: float = 0
    week: int = 1
    category: str | None = None
    rate: float = 0
    price_change: float = 0
    demand_response: float = 0
    extra_cost: float = 0


@app.post("/scenario")
def scenario(req: ScenarioRequest):
    s = get_session(req.session_id)
    weekly = s["weekly"]
    cash_now = float(weekly["ending_cash"].iloc[-1])
    inflow, outflow = baseline_table(weekly)
    base = summarize(inflow, outflow, cash_now, s["cushion"])

    if req.name == "slow_season":
        new_in, new_out = slow_season(inflow, outflow, req.drop, req.start, req.length)
    elif req.name == "cost_shock" and req.category:
        if req.category not in weekly.columns:
            raise HTTPException(status_code=400, detail="Unknown category.")
        category_forecast = seasonal_naive(weekly[req.category])
        new_in, new_out = cost_shock_recurring(inflow, outflow, category_forecast, req.rate, req.week)
    elif req.name == "cost_shock":
        new_in, new_out = cost_shock_one_time(inflow, outflow, req.amount, req.week)
    else:
        new_in, new_out = decision_lever(
            inflow, outflow, req.price_change, req.demand_response, req.extra_cost, req.week
        )

    changed = summarize(new_in, new_out, cash_now, s["cushion"])           

    result = {
        "baseline": base,
        "scenario": changed,
        "change": {
            "lowest_cash": round(changed["lowest_cash"] - base["lowest_cash"], 2),
            "net_13_weeks": round(changed["net_13_weeks"] - base["net_13_weeks"], 2),
        },
        "ending_cash": {
            "baseline": [round(float(x), 2) for x in cash_now + np.cumsum(inflow - outflow)],
            "scenario": [round(float(x), 2) for x in cash_now + np.cumsum(new_in - new_out)],
        },
        "disclaimer": DISCLAIMER,
    }
    if req.name == "decision_lever":
        result["break_even_lift"] = break_even_lift(inflow, req.extra_cost)
    return result

ASK_LIMIT = 10
ASK_WINDOW = 60
recent_asks = {}


class AskRequest(BaseModel):
    session_id: str
    question: str


class FeedbackRequest(BaseModel):
    exchange_id: int
    helpful: bool

@app.post("/ask")
def ask_endpoint(req: AskRequest):
    s = get_session(req.session_id)
    now = time.time()
    history = [t for t in recent_asks.get(req.session_id, []) if now - t < ASK_WINDOW]
    if len(history) >= ASK_LIMIT:
        raise HTTPException(status_code=____, detail="Too many questions. Please wait a minute.")    # BLANK
    recent_asks[req.session_id] = history + [now]

    result = run_agent(GroqProvider(), req.question, s["weekly"], s["cushion"])
    check = check_answer(result["answer"], result["tool_outputs"])
    row_id = log_exchange(req.question, result["tool_outputs"], result["answer"], check["faithful"], result["tokens"])
    return {
        "answer": result["answer"],
        "exchange_id": row_id,
        "faithful": check["faithful"],
        "disclaimer": DISCLAIMER,
    }


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    set_feedback(req.exchange_id, 1 if req.helpful else 0)
    return {"counts": feedback_counts()}