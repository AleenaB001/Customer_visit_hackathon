import streamlit as st
import pandas as pd

def kb_card(retrieved_kb: list):

    with st.container(border=True):

        st.subheader("📚 KB Articles — Retrieved Chunks")

        if not retrieved_kb:
            st.info("No KB chunks retrieved.")
            return

        rows = []

        for i, chunk in enumerate(retrieved_kb, start=1):
            meta  = chunk.get("meta", {})
            kb_no = meta.get("kb", "—")
            title = meta.get("title", "—")
            score = chunk.get("score", 0)
            text  = chunk.get("text", "")

            preview = text[:120] + "..." if len(text) > 120 else text

            rows.append({
                "#":       i,
                "KB":      kb_no,
                "Title":   title,
                "Preview": preview,
                "Score":   f"{score}%"
            })

        df = pd.DataFrame(rows)

        st.dataframe(df, use_container_width=True, hide_index=True)

        