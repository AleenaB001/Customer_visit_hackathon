import sqlite3

DB = "backend/history.sqlite"


def initialize_queue():

    conn = sqlite3.connect(DB)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS incident_queue(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        incident_number TEXT UNIQUE,

        category TEXT,

        priority TEXT,

        state TEXT,

        short_description TEXT,

        description TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        processed INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def add_incident(incident):

    conn = sqlite3.connect(DB)

    conn.execute("""
    INSERT OR IGNORE INTO incident_queue(

        incident_number,
        category,
        priority,
        state,
        short_description,
        description

    )

    VALUES(?,?,?,?,?,?)
    """,

    (

        incident["number"],
        incident["category"],
        incident["priority"],
        incident["state"],
        incident["short_description"],
        incident["description"]

    ))

    conn.commit()

    conn.close()


def get_pending_incidents():

    conn = sqlite3.connect(DB)

    conn.row_factory = sqlite3.Row

    rows = conn.execute("""

    SELECT *

    FROM incident_queue

    WHERE processed=0

    ORDER BY created_at DESC

    """).fetchall()

    conn.close()

    return [dict(r) for r in rows]


def get_latest_pending():

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    row = conn.execute("""
        SELECT *
        FROM incident_queue
        WHERE processed = 0
        ORDER BY created_at DESC
        LIMIT 1
    """).fetchone()

    conn.close()

    if row:
        return dict(row)

    return None


def mark_processed(incident_number):

    conn = sqlite3.connect(DB)

    conn.execute("""

    UPDATE incident_queue

    SET processed=1

    WHERE incident_number=?

    """, (incident_number,))

    conn.commit()

    conn.close()


def get_all_pending() -> list[dict]:
    """
    Returns ALL rows in incident_queue where processed = 0,
    ordered by created_at DESC (newest first).
    """
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT *
        FROM   incident_queue
        WHERE  processed = 0
        ORDER  BY created_at DESC
        """
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows