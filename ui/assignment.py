import streamlit as st

def assignment_card():

    st.subheader("👤 Assignment Recommendation")

    st.success("Suggested Assignment Group")

    st.code("End User Support")

    st.metric(
        "Estimated MTTR Saved",
        "25 Minutes"
    )

    st.button("Generate Resolution Notes")