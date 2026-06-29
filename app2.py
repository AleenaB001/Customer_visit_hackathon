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
# 📑 Tab Layout Setup
# ==========================================================
tab1, tab2 = st.tabs(["📋 All Incidents", "🧠 AI Resolution Workspace"])

# ==========================================================
# Tab 1: All Incidents (Limit 20)
# ==========================================================
with tab1:
    st.subheader("Latest 20 Incidents")
    try:
        all_incidents = get_all_incidents(limit=20)
        
        if not all_incidents:
            st.info("No incidents found in ServiceNow.")
        else:
            # Display a clean data table for overview
            st.dataframe(
                all_incidents, 
                use_container_width=True,
                column_config={
                    "number": "Incident Number",
                    "priority": "Priority",
                    "state": "State",
                    "category": "Category",
                    "short_description": "Short Description"
                }
            )
            
            # Interactive dropdown selector to inspect/analyze a specific incident
            st.markdown("### 🔍 Select an Incident to Analyze in Tab 2")
            incident_options = {f"{inc['number']} - {inc['short_description'][:50]}...": inc for inc in all_incidents}
            
            selected_option = st.selectbox(
                "Choose an incident from the list:", 
                options=list(incident_options.keys()),
                index=0
            )
            
            if selected_option:
                # Store full detailed mapping to pass into the AI engine
                st.session_state["selected_incident"] = incident_options[selected_option]
                st.success(f"Selected {st.session_state['selected_incident']['number']}. Switch to the 'AI Resolution Workspace' tab to view analysis.")

    except Exception as e:
        st.error(f"Unable to fetch all incidents: {e}")

# ==========================================================
# Tab 2: AI Resolution Workspace
# ==========================================================
with tab2:
    # Fetch Target Incident
    try:
        if "selected_incident" in st.session_state:
            incident = st.session_state["selected_incident"]
        else:
            # Fallback to latest single incident if nothing is selected yet
            incident = get_latest_incident()

        if incident is None:
            st.warning("No incidents found.")
            st.stop()

    except Exception as e:
        st.error(f"Unable to fetch incident\n\n{e}")
        st.stop()

    # Active Incident Banner
    st.info(f"👉 Currently Analyzing: **{incident.get('number')}** — {incident.get('short_description')}")

    # Gemini Analysis
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

    retrieved_kb = ai_response.get("retrieved_kb", [])
    retrieved_incidents = ai_response.get("retrieved_incidents", [])

    # Main Split Layout
    left, right = st.columns([2, 3], gap="large")

    with left:
        incident_card(incident)

    with right:
        auto_resolution_card(incident, ai_response)

    st.divider()

    # Bottom Tri-Fold Panel
    c1, c2, c3 = st.columns(3)

    with c1:
        kb_card(retrieved_kb)

    with c2:
        similar_incidents_card(retrieved_incidents)

    with c3:
        reasoning_card(ai_response)

st.divider()
st.caption("Powered by ServiceNow • Gemini • ChromaDB")