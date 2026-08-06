import streamlit as st


class Filters:

    @staticmethod
    def show(df):

        st.sidebar.title("🔍 Filters")

        corridor = st.sidebar.selectbox(
            "Corridor",
            ["All"] + sorted(df["corridor_id"].unique().tolist())
        )

        direction = st.sidebar.selectbox(
            "Direction",
            ["All"] + sorted(df["direction"].unique().tolist())
        )

        return corridor, direction