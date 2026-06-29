import streamlit as st

def root_cause_card():

    st.subheader("🔍 Root Cause")

    st.table({

        "Possible Cause":[
            "USB Driver",
            "USB Port Failure",
            "Power Issue",
            "Device Compatibility"
        ],

        "Confidence":[
            "92%",
            "81%",
            "67%",
            "60%"
        ]

    })