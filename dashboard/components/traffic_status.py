import streamlit as st


class TrafficStatus:

    @staticmethod
    def show(engine):

        st.subheader("🚦 Traffic Status")

        df = engine.traffic_status()

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )