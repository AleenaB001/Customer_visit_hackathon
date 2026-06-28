import streamlit as st
import pandas as pd


def similar_incidents_card(similar_incidents):

    with st.container(border=True):

        st.subheader("🔄 Similar Incidents")

        if not similar_incidents:
            st.info("No similar incidents found.")
            return

        # If Gemini returns only incident numbers
        if isinstance(similar_incidents[0], str):

            df = pd.DataFrame(
                {"Incident Number": similar_incidents}
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            return

        # Old ServiceNow format
        df = pd.DataFrame(similar_incidents)

        columns = [
            "number",
            "priority",
            "state",
            "category",
            "short_description"
        ]

        columns = [c for c in columns if c in df.columns]

        st.dataframe(
            df[columns],
            use_container_width=True,
            hide_index=True
        )