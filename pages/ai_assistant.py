import streamlit as st
from backend.history_db import initialize_database
# -----------------------------
# Backend
# -----------------------------
from backend.service_now import (
    get_latest_incident,
    get_all_incidents,
    get_kb_articles
)

from backend.gemini_services import generate_resolution


# -----------------------------
# UI
# -----------------------------
from ui.incident_card import incident_card
from ui.auto_resolution import auto_resolution_card
from ui.kb_articles import kb_card
from ui.similar_incidents import similar_incidents_card
from ui.ui_reasoning import reasoning_card

from backend.history_db import (
    initialize_database,
    save_ai_resolution,
    save_engineer_notes
)


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Incident Resolution Assistant",
    page_icon="🤖",
    layout="wide"
)
initialize_database()
st.title("🤖 AI Incident Resolution Assistant")
st.caption("AI-powered L2 Incident Resolution")


# ==========================================================
# Fetch Latest Incident
# ==========================================================

try:
    incident = get_latest_incident()

    if incident is None:
        st.warning("No incidents found.")
        st.stop()

except Exception as e:
    st.error(f"Unable to fetch incident\n\n{e}")
    st.stop()


# ==========================================================
# Gemini Analysis
# ==========================================================

try:
    ai_response = generate_resolution(incident)

except Exception as e:

    st.error(f"Gemini Error\n\n{e}")

    ai_response = {
        "summary": "",
        "root_cause": "",
        "resolution_steps": [],
        "confidence": 0,
        "escalation": "",
        "kb_used": []
    }


# ==========================================================
# KB Articles
# ==========================================================

try:

    kb_articles = get_kb_articles()

except Exception:

    kb_articles = []


# ==========================================================
# Similar Incidents
# ==========================================================

# ==========================================================
# Similar Incidents
# ==========================================================

try:

    similar_incidents = get_all_incidents(limit=5)

except Exception:

    similar_incidents = []


# ==========================================================
# Layout
# ==========================================================

left, right = st.columns([2,3], gap="large")

with left:

    incident_card(incident)

with right:

    auto_resolution_card(
        incident,
        ai_response
    )

st.divider()

c1, c2, c3 = st.columns(3)

with c1:

    kb_card(kb_articles)

with c2:

    similar_incidents_card(similar_incidents)

with c3:

    reasoning_card(ai_response)


st.divider()

st.caption("Powered by ServiceNow • Gemini • ChromaDB")