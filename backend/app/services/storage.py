"""SQLite storage for analysis history (keeps the newest HISTORY_LIMIT rows)."""
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from ..config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
  id TEXT PRIMARY KEY, created_at TEXT NOT NULL, mode TEXT NOT NULL DEFAULT 'single',
  fruit_type TEXT, grade TEXT, score INTEGER, ripeness TEXT, defect_count INTEGER,
  recommendation_key TEXT, payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at DESC);
"""


@contextmanager
def conn():
    c = sqlite3.connect(settings.db_path, timeout=10)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db():
    with conn() as c:
        c.executescript(SCHEMA)


def _delete_files(analysis_id: str):
    for suffix in ("_orig.jpg", "_annotated.jpg"):
        p = settings.outputs_dir / f"{analysis_id}{suffix}"
        if p.exists():
            p.unlink()


def save_analysis(result: dict, mode: str = "single") -> str:
    analysis_id = uuid.uuid4().hex[:12]
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result = {**result, "id": analysis_id, "created_at": created, "mode": mode}
    with conn() as c:
        c.execute("INSERT INTO analyses VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (analysis_id, created, mode, result["fruit_type"], result["grade"], result["score"],
                   result["ripeness"]["label"], len(result["defects"]), result["recommendation_key"], json.dumps(result)))
        old = c.execute("SELECT id FROM analyses ORDER BY created_at DESC, rowid DESC LIMIT -1 OFFSET ?",
                        (settings.history_limit,)).fetchall()
        for row in old:
            c.execute("DELETE FROM analyses WHERE id=?", (row["id"],))
            _delete_files(row["id"])
    return analysis_id


def get_analysis(analysis_id: str) -> dict | None:
    with conn() as c:
        row = c.execute("SELECT payload FROM analyses WHERE id=?", (analysis_id,)).fetchone()
    return json.loads(row["payload"]) if row else None


def list_history() -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT id, created_at, mode, fruit_type, grade, score, ripeness, defect_count, recommendation_key "
                         "FROM analyses ORDER BY created_at DESC, rowid DESC").fetchall()
    return [dict(r) for r in rows]


def delete_analysis(analysis_id: str) -> bool:
    with conn() as c:
        n = c.execute("DELETE FROM analyses WHERE id=?", (analysis_id,)).rowcount
    if n:
        _delete_files(analysis_id)
    return bool(n)
