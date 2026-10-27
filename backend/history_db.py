"""Save and fetch each user's past reviews, in a local SQLite file (history.db)."""
import sqlite3, json, datetime

DB_FILE = "history.db"

def _conn():
    c = sqlite3.connect(DB_FILE)
    c.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        created_at TEXT NOT NULL,
        file_name TEXT,
        n_functions INTEGER,
        n_high INTEGER,
        report_json TEXT NOT NULL
    )""")
    return c

def save_review(username, report, file_name="input.py"):
    n_high = sum(f["level"] == "HIGH" for f in report["functions"])
    with _conn() as c:
        c.execute("INSERT INTO reviews (username, created_at, file_name, n_functions, n_high, report_json) "
                  "VALUES (?,?,?,?,?,?)",
                  (username, datetime.datetime.now().isoformat(timespec="seconds"),
                   file_name, len(report["functions"]), n_high, json.dumps(report)))

def list_reviews(username, limit=50):
    with _conn() as c:
        rows = c.execute("SELECT id, created_at, file_name, n_functions, n_high FROM reviews "
                         "WHERE username=? ORDER BY id DESC LIMIT ?", (username, limit)).fetchall()
    return [{"id": r[0], "created_at": r[1], "file_name": r[2], "n_functions": r[3], "n_high": r[4]} for r in rows]

def get_review(review_id, username):
    with _conn() as c:
        row = c.execute("SELECT report_json FROM reviews WHERE id=? AND username=?",
                        (review_id, username)).fetchone()
    return json.loads(row[0]) if row else None