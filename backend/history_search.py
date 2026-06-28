import sqlite3

DB = "backend/history.sqlite"


def search_history(category, short_description):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            incident_number,
            root_cause,
            resolution_steps,
            kb_used
        FROM incident_history
        WHERE category=?
        ORDER BY created_at DESC
        LIMIT 5
    """, (category,))

    rows = cursor.fetchall()

    conn.close()

    return rows