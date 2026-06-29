import streamlit as st

def resolution_card():

    st.subheader("🛠 Recommended Resolution")

    st.checkbox("Try another USB port")

    st.checkbox("Restart Computer")

    st.checkbox("Update USB Drivers")

    st.checkbox("Enable USB Root Hub")

    st.checkbox("Run Hardware Troubleshooter")