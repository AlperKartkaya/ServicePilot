"""SQLite persistence (NFR-3): case JSON blobs + settings key/value. No ORM (ADR-1)."""
import json
import sqlite3
from pathlib import Path

from .catalog import DEFAULT_SETTINGS

DB = Path(__file__).resolve().parent.parent / "data" / "servicepilot.db"
DB.parent.mkdir(exist_ok=True)


def _conn():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, data TEXT NOT NULL, created_at TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    return c


def save_case(case):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO cases VALUES (?, ?, ?)", (case["id"], json.dumps(case, ensure_ascii=False), case["created_at"]))


def get_case(cid):
    with _conn() as c:
        row = c.execute("SELECT data FROM cases WHERE id = ?", (cid,)).fetchone()
    return json.loads(row[0]) if row else None


def list_cases():
    with _conn() as c:
        return [json.loads(r[0]) for r in c.execute("SELECT data FROM cases ORDER BY created_at DESC")]


def next_id():
    with _conn() as c:
        n = c.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        while c.execute("SELECT 1 FROM cases WHERE id = ?", (f"SP-{n + 1:04d}",)).fetchone():
            n += 1
    return f"SP-{n + 1:04d}"


def delete_cases():
    with _conn() as c:
        return c.execute("DELETE FROM cases").rowcount


def get_settings():
    with _conn() as c:
        row = c.execute("SELECT value FROM kv WHERE key = 'settings'").fetchone()
    return {**DEFAULT_SETTINGS, **(json.loads(row[0]) if row else {})}


def save_settings(s):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO kv VALUES ('settings', ?)", (json.dumps(s),))
    return s
