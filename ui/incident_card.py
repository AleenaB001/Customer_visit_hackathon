import streamlit as st

def incident_card(data):

    with st.container(border=True):

        st.subheader("📥 Latest Incident")

        st.metric("Incident", data["number"])

        c1, c2 = st.columns(2)

        c1.metric("Priority", data["priority"])
        c2.metric("State", data["state"])

        st.write("**Category**")
        st.write(data["category"])

        st.write("**Short Description**")
        st.info(data["short_description"])

        st.write("**Description**")
        st.write(data["description"])

        st.caption(f"Opened : {data['opened_at']}")