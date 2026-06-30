
import streamlit as st

# -----------------------------
# Backend
# -----------------------------
from backend.service_now import (
    get_latest_incident,
    get_all_incidents,
)

from backend.gemini_services import generate_resolution
from backend.history_db import initialize_database

# -----------------------------
# UI Components
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
# Theme
# ==========================================================

THEME = {
    "navy": "#0A0F1E",
    "card": "#0D1B2A",
    "card2": "#112236",
    "border": "#1E3A5F",
    "blue": "#1565C0",
    "cyan": "#00E5FF",
    "green": "#00C853",
    "red": "#FF1744",
    "amber": "#FFB300",
    "text_high": "#E8F4FD",
    "text_mid": "#7EA8C4",
}

st.markdown(
f"""
<style>

.stApp {{
    background-color:{THEME['navy']};
    color:{THEME['text_high']};
}}

h1,h2,h3,h4,p,span,label {{
    color:{THEME['text_high']};
}}

.block-container {{
    padding-top:1rem;
    padding-bottom:1rem;
}}

div[data-testid="stVerticalBlock"] {{
    gap:0.4rem;
}}

.stButton > button {{
    width:100%;
    height:35px;
    border-radius:8px;
    padding:0.2rem;
    background-color:{THEME['card2']};
    color:{THEME['text_high']};
    border:1px solid {THEME['border']};
}}

.stButton > button:hover {{
    border:1px solid {THEME['cyan']};
    color:{THEME['cyan']};
}}

[data-testid="stAlert"] {{
    background-color:{THEME['card']};
    border:1px solid {THEME['border']};
}}

</style>
""",
unsafe_allow_html=True
)


# ==========================================================
# Notification Panel
# ==========================================================

@st.fragment(run_every=60)
def auto_refresh_notifications():
    notification_panel()

auto_refresh_notifications()

st.title("🤖 AI Incident Resolution Assistant")
st.caption("AI-powered L2 Incident Resolution")


# ==========================================================
# Compact Incident Table
# ==========================================================

if "selected_incident" not in st.session_state:

    st.subheader("📋 Latest 20 Incidents")

    try:

        all_incidents = get_all_incidents(limit=20)

        if not all_incidents:
            st.info("No incidents found.")

        else:

            h1,h2,h3,h4 = st.columns([2,5,2,1])

            h1.markdown("**Incident**")
            h2.markdown("**Description**")
            h3.markdown("**Priority**")
            h4.markdown("**Action**")

            st.markdown("---")

            for inc in all_incidents:

                c1,c2,c3,c4 = st.columns(
                    [2,5,2,1],
                    vertical_alignment="center"
                )

                with c1:
                    st.markdown(
                        f"**{inc['number']}**"
                    )

                with c2:

                    desc = inc.get(
                        "short_description",
                        ""
                    )

                    if len(desc) > 80:
                        desc = desc[:80] + "..."

                    st.caption(desc)

                with c3:

                    priority = str(
                        inc.get(
                            "priority",
                            "N/A"
                        )
                    )

                    color_map = {
                        "1":THEME["red"],
                        "2":THEME["amber"],
                        "3":THEME["green"]
                    }

                    color = color_map.get(
                        priority,
                        THEME["cyan"]
                    )

                    st.markdown(
                        f"""
                        <div style="
                            background:{color};
                            padding:4px;
                            text-align:center;
                            border-radius:10px;
                            width:60px;
                        ">
                        P{priority}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c4:

                    if st.button(
                        "🔍",
                        key=inc["number"],
                        help="Analyze Incident"
                    ):

                        st.session_state[
                            "selected_incident"
                        ] = inc

                        st.rerun()

                st.markdown(
                    "<hr style='margin:4px'>",
                    unsafe_allow_html=True
                )

    except Exception as e:

        st.error(
            f"Unable to fetch incidents: {e}"
        )


# ==========================================================
# AI Resolution Workspace
# ==========================================================

else:

    incident = st.session_state["selected_incident"]

    col1,col2 = st.columns([1,6])

    with col1:

        if st.button("⬅ Back"):

            del st.session_state["selected_incident"]
            st.rerun()

    with col2:

        st.info(
            f"""
            👉 Currently Analyzing:
            {incident.get('number')}
            — {incident.get('short_description')}
            """
        )

    try:

        ai_response = generate_resolution(
            incident
        )

    except Exception as e:

        st.error(f"Gemini Error: {e}")

        ai_response={
            "summary":"",
            "root_cause":"",
            "resolution_steps":[],
            "confidence":0,
            "escalation":"",
            "kb_used":[],
            "retrieved_kb":[],
            "retrieved_incidents":[]
        }

    retrieved_kb=ai_response.get(
        "retrieved_kb",[]
    )

    retrieved_incidents=ai_response.get(
        "retrieved_incidents",[]
    )

    left,right=st.columns(
        [2,3],
        gap="large"
    )

    with left:
        incident_card(incident)

    with right:
        auto_resolution_card(
            incident,
            ai_response
        )

    st.divider()

    c1,c2,c3=st.columns(3)

    with c1:
        kb_card(retrieved_kb)

    with c2:
        similar_incidents_card(
            retrieved_incidents
        )

    with c3:
        reasoning_card(ai_response)

st.divider()

st.caption(
    "Powered by ServiceNow • Gemini • ChromaDB"
)
