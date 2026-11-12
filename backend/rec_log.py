import json
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "recommendations.db"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS exchanges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created REAL,
            question TEXT,
            tool_calls TEXT,
            answer TEXT,
            faithful INTEGER,
            tokens INTEGER,
            feedback INTEGER
        )"""
    )
    return conn


def log_exchange(question, tool_outputs, answer, faithful, tokens):
    conn = connect()
    cursor = conn.execute(
        "INSERT INTO exchanges (created, question, tool_calls, answer, faithful, tokens, feedback) "
        "VALUES (?, ?, ?, ?, ?, ?, NULL)",
        (time.time(), question, json.dumps(tool_outputs), answer, int(faithful), tokens),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def set_feedback(row_id, value):
    conn = connect()
    conn.execute("UPDATE exchanges SET feedback = ? WHERE id = ?", (value, row_id))      
    conn.commit()
    conn.close()


def feedback_counts():
    conn = connect()
    rows = conn.execute("SELECT feedback, COUNT(*) FROM exchanges WHERE feedback IS NOT NULL GROUP BY feedback").fetchall()
    conn.close()
    return {("up" if value == 1 else "down"): count for value, count in rows}