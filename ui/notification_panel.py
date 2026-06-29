"""
ui/notification_panel.py
Polls ServiceNow directly — no queue, no SQLite.
"""

import streamlit as st
from backend.service_now import get_new_incidents

PRIORITY_COLOR = {
    "1 - Critical": "#FF4B4B",
    "2 - High":     "#FF8C00",
    "3 - Moderate": "#FFC300",
    "4 - Low":      "#21BA45",
}

PRIORITY_ICON = {
    "1 - Critical": "🔴",
    "2 - High":     "🟠",
    "3 - Moderate": "🟡",
    "4 - Low":      "🟢",
}


def _badge_css(count: int) -> str:
    return f"""
    <style>
    .notif-badge {{
        position: fixed;
        top: 56px;
        right: 24px;
        background: #FF4B4B;
        color: white;
        border-radius: 50%;
        width: 22px;
        height: 22px;
        font-size: 12px;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        box-shadow: 0 2px 6px rgba(0,0,0,.35);
        pointer-events: none;
    }}
    </style>
    {"<div class='notif-badge'>" + str(count) + "</div>" if count > 0 else ""}
    """


def notification_panel():

    # ── init state ────────────────────────────────────────────────────────────
    if "notif_drawer_open" not in st.session_state:
        st.session_state["notif_drawer_open"] = False

    if "notif_dismissed" not in st.session_state:
        st.session_state["notif_dismissed"] = set()   # track dismissed inc numbers

    if "notif_run" not in st.session_state:
        st.session_state["notif_run"] = 0
    st.session_state["notif_run"] += 1
    run = st.session_state["notif_run"]

    # ── fetch directly from ServiceNow (last 5 minutes) ─────────────────────
    try:
        all_new = get_new_incidents(since_minutes=5)
    except Exception as e:
        all_new = []

    # Filter out incidents the user already opened this session
    dismissed = st.session_state["notif_dismissed"]
    pending_list = [i for i in all_new if i["number"] not in dismissed]
    count = len(pending_list)

    # ── badge ─────────────────────────────────────────────────────────────────
    st.markdown(_badge_css(count), unsafe_allow_html=True)

    # ── bell button ───────────────────────────────────────────────────────────
    bell_label = f"🔔  Notifications {'(' + str(count) + ' new)' if count else ''}"

    with st.container():
        _, col_bell = st.columns([10, 2])
        with col_bell:
            if st.button(
                bell_label,
                key=f"notif_bell_{run}",
                type="secondary",
                use_container_width=True,
            ):
                st.session_state["notif_drawer_open"] = (
                    not st.session_state["notif_drawer_open"]
                )
                st.rerun()

    # ── sidebar drawer ────────────────────────────────────────────────────────
    if st.session_state["notif_drawer_open"]:
        with st.sidebar:
            st.markdown("## 🔔 New Incidents")

            if not pending_list:
                st.info("No new incidents found in ServiceNow.")
            else:
                for item in pending_list:
                    priority   = item.get("priority", "4 - Low")
                    color      = PRIORITY_COLOR.get(priority, "#21BA45")
                    icon       = PRIORITY_ICON.get(priority, "🟢")
                    inc_num    = item.get("number", "—")
                    short_desc = item.get("short_description", "No description")
                    category   = item.get("category", "")
                    opened_at  = item.get("opened_at", "")

                    with st.container(border=True):
                        st.markdown(
                            f"<span style='color:{color};font-weight:700'>"
                            f"{icon} {inc_num}</span>",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"{priority}  •  {category}  •  {opened_at}")
                        st.write(short_desc[:80] + ("…" if len(short_desc) > 80 else ""))

                        if st.button(
                            "⚡ Open AI Resolution",
                            key=f"open_{inc_num}_{run}",
                            type="primary",
                            use_container_width=True,
                        ):
                            st.session_state["selected_incident"] = {
                                "number":            inc_num,
                                "priority":          priority,
                                "state":             item.get("state", "New"),
                                "category":          category,
                                "short_description": short_desc,
                                "description":       item.get("description", ""),
                            }
                            # Mark as dismissed so badge count drops
                            st.session_state["notif_dismissed"].add(inc_num)
                            st.session_state["notif_drawer_open"] = False
                            st.rerun()

            st.divider()
            if st.button("✖ Close", key=f"close_drawer_{run}"):
                st.session_state["notif_drawer_open"] = False
                st.rerun()