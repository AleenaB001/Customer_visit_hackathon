import streamlit as st
import pandas as pd

def kb_card(kb_articles):

    with st.container(border=True):

        st.subheader("📚 KB Articles")

        df = pd.DataFrame({

            "KB":[
                "KB001",
                "KB024",
                "KB105"
            ],

            "Title":[
                "USB Device Not Recognized",
                "USB Driver Installation",
                "Hardware Diagnostics"
            ],

            "Match":[
                "98%",
                "92%",
                "81%"
            ]

        })

        st.dataframe(df, use_container_width=True, hide_index=True)