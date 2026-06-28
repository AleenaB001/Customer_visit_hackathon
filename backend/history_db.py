import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "history.sqlite")


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incident_history (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        incident_number TEXT,

        category TEXT,

        short_description TEXT,

        description TEXT,

        ai_summary TEXT,

        ai_root_cause TEXT,

        ai_resolution TEXT,

        engineer_notes TEXT,

        final_resolution TEXT,

        approved INTEGER DEFAULT 0,

        resolution_source TEXT,

        kb_used TEXT,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()


def save_ai_resolution(incident, ai):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO incident_history(

        incident_number,
        category,
        short_description,
        description,

        ai_summary,
        ai_root_cause,
        ai_resolution,

        approved,

        resolution_source,

        kb_used

    )

    VALUES(?,?,?,?,?,?,?,?,?,?)

    """, (

        incident["number"],

        incident["category"],

        incident["short_description"],

        incident["description"],

        ai.get("summary",""),

        ai.get("root_cause",""),

        json.dumps(ai.get("resolution_steps",[])),

        1,

        "AI",

        json.dumps(ai.get("kb_used",[]))

    ))

    conn.commit()

    conn.close()


def save_engineer_notes(

        incident,

        ai,

        notes

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO incident_history(

        incident_number,
        category,
        short_description,
        description,

        ai_summary,
        ai_root_cause,
        ai_resolution,

        engineer_notes,

        final_resolution,

        approved,

        resolution_source,

        kb_used

    )

    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)

    """, (

        incident["number"],

        incident["category"],

        incident["short_description"],

        incident["description"],

        ai.get("summary",""),

        ai.get("root_cause",""),

        json.dumps(ai.get("resolution_steps",[])),

        notes,

        notes,

        1,

        "ENGINEER",

        json.dumps(ai.get("kb_used",[]))

    ))

    conn.commit()

    conn.close()


def get_recent_history(limit=20):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

    incident_number,

    category,

    short_description,

    resolution_source,

    approved,

    created_at

    FROM incident_history

    ORDER BY created_at DESC

    LIMIT ?

    """,(limit,))

    rows = cursor.fetchall()

    conn.close()

    return rows