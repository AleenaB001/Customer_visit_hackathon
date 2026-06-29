import streamlit as st

def summary_card():

    st.subheader("🧠 AI Summary")

    st.success("""

The incident indicates a USB connectivity issue.

Based on similar incidents, the most probable causes are:

• Driver corruption

• USB Controller issue

• Hardware failure

Initial troubleshooting can resolve this without escalation.

""")