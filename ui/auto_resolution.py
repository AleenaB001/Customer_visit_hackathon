import streamlit as st

from backend.history_db import (
    save_ai_resolution,
    save_engineer_notes
)


def auto_resolution_card(
        incident,
        ai
):

    with st.container(border=True):

        st.subheader("🤖 AI Auto Resolution")

        st.markdown("### 🧠 AI Summary")

        st.info(
            ai.get("summary", "")
        )

        st.markdown("### 🔍 Root Cause")

        st.write(
            ai.get("root_cause", "")
        )

        confidence = ai.get("confidence", 0)

        st.progress(confidence / 100)

        st.markdown("---")

        st.markdown("### 🛠 Resolution Steps")

        steps = ai.get(
            "resolution_steps",
            []
        )

        if steps:

            for i, step in enumerate(steps, 1):

                st.write(f"{i}. {step}")

        else:

            st.info("No steps generated.")

        st.markdown("---")

        st.markdown("### ✍ Engineer Work Notes")

        notes = st.text_area(
            "Add troubleshooting notes",
            height=150
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "✅ Approve AI Resolution",
                use_container_width=True
            ):

                save_ai_resolution(
                    incident,
                    ai
                )

                st.success(
                    "AI Resolution Saved!"
                )

        with c2:

            if st.button(
                "💾 Save Engineer Notes",
                use_container_width=True
            ):

                if notes.strip():

                    save_engineer_notes(
                        incident,
                        ai,
                        notes
                    )

                    st.success(
                        "Engineer Notes Saved!"
                    )

                else:

                    st.warning(
                        "Please enter work notes."
                    )