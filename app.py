import streamlit as st

# -----------------------------
# Backend
# -----------------------------
from backend.service_now import (
    get_latest_incident,
    get_all_incidents,
    get_kb_articles,
    get_similar_incidents
)

from backend.gemini_services import generate_resolution
from backend.history_db import initialize_database

# -----------------------------
# UI
# -----------------------------
from ui.incident_card import incident_card
from ui.auto_resolution import auto_resolution_card
from ui.kb_articles import kb_card
from ui.similar_incidents import similar_incidents_card
from ui.ui_reasoning import reasoning_card
from ui.notification_panel import notification_panel

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Incident Resolution Assistant",
    page_icon="🤖",
    layout="wide"
)

initialize_database()

# ==========================================================
# 🔔 Notification Panel — polls ServiceNow directly
# ==========================================================

@st.fragment(run_every=60)
def auto_refresh_notifications():
    notification_panel()

auto_refresh_notifications()

st.title("🤖 AI Incident Resolution Assistant")
st.caption("AI-powered L2 Incident Resolution")

# ==========================================================
# Fetch Incident
# ==========================================================

try:
    if "selected_incident" in st.session_state:
        incident = st.session_state["selected_incident"]
    else:
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
        "kb_used": [],
        "retrieved_kb": [],
        "retrieved_incidents": []
    }

# ==========================================================
# Retrieved Chunks (already formatted by gemini_services)
# ==========================================================

retrieved_kb        = ai_response.get("retrieved_kb", [])
retrieved_incidents = ai_response.get("retrieved_incidents", [])

# ==========================================================
# Layout
# ==========================================================

left, right = st.columns([2, 3], gap="large")

with left:
    incident_card(incident)

with right:
    auto_resolution_card(incident, ai_response)

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    kb_card(retrieved_kb)

with c2:
    similar_incidents_card(retrieved_incidents)

with c3:
    reasoning_card(ai_response)

st.divider()

st.caption("Powered by ServiceNow • Gemini • ChromaDB")