import streamlit as st


def reasoning_card(ai):

    with st.container(border=True):

        st.subheader("🧠 AI Insights")

        st.metric(
            "Confidence",
            f"{ai.get('confidence', 0)}%"
        )

        st.markdown("### Escalation")

        escalation = ai.get("escalation", "Unknown")

        if escalation.lower() == "no":
            st.success("No Escalation Required")
        else:
            st.warning("Escalation Recommended")

        st.markdown("### Knowledge Used")

        kb = ai.get("kb_used", [])

        if kb:

            for article in kb:
                st.write(f"• {article}")

        else:

            st.info("No KB Articles Referenced")