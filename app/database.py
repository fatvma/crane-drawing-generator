"""All database code lives here (SQLite, using Python's built-in sqlite3).

Every SQL statement uses ? placeholders and passes values separately.
This stops SQL injection: user text is never glued into the SQL string.
"""

import os
import sqlite3
from datetime import datetime, timezone

# The database file. Can be changed with an environment variable.
# *.db files are listed in .gitignore, so this file is not committed.
DB_PATH = os.environ.get("CRANE_DB_PATH", "crane_designs.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS designs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL,
    span_m            REAL NOT NULL,
    capacity_t        REAL NOT NULL,
    lifting_height_m  REAL NOT NULL,
    duty_group        TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
)
"""


def connect(path=None):
    """Open a connection. Rows can be read like dictionaries."""
    # check_same_thread=False: FastAPI may use the connection from another
    # thread. We open one connection per request, so this is safe.
    conn = sqlite3.connect(path or DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    """Create the table if it does not exist yet."""
    with conn:
        conn.execute(SCHEMA)


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def create_design(conn, name, inputs):
    now = _now()
    with conn:  # saves (commits) if no error, undoes everything if there is one
        cursor = conn.execute(
            "INSERT INTO designs (name, span_m, capacity_t, lifting_height_m, "
            "duty_group, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, inputs["span_m"], inputs["capacity_t"],
             inputs["lifting_height_m"], inputs["duty_group"], now, now),
        )
    return get_design(conn, cursor.lastrowid)


def get_design(conn, design_id):
    """Returns the row, or None if there is no such design."""
    return conn.execute(
        "SELECT * FROM designs WHERE id = ?", (design_id,)
    ).fetchone()


def list_designs(conn):
    """Most recently changed first."""
    return conn.execute(
        "SELECT * FROM designs ORDER BY updated_at DESC, id DESC"
    ).fetchall()


def update_design(conn, design_id, name, inputs):
    """Returns the updated row, or None if there is no such design."""
    with conn:
        cursor = conn.execute(
            "UPDATE designs SET name = ?, span_m = ?, capacity_t = ?, "
            "lifting_height_m = ?, duty_group = ?, updated_at = ? WHERE id = ?",
            (name, inputs["span_m"], inputs["capacity_t"],
             inputs["lifting_height_m"], inputs["duty_group"], _now(), design_id),
        )
    if cursor.rowcount == 0:
        return None
    return get_design(conn, design_id)