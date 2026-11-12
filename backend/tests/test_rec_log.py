import sys

sys.path.insert(0, "backend")

import rec_log


def test_exchange_is_logged_and_feedback_counted(tmp_path, monkeypatch):
    monkeypatch.setattr(rec_log, "DB_PATH", tmp_path / "test.db")
    row = rec_log.log_exchange("How am I doing?", [{"cash_now": 100}], "Fine.", True, 50)
    rec_log.set_feedback(row, 1)
    assert rec_log.feedback_counts() == {"up": 1}              