import streamlit as st


class CorridorRanking:

    @staticmethod
    def show(engine):

        st.subheader("🏆 Corridor Performance Ranking")

        ranking = engine.corridor_ranking()

        st.dataframe(
            ranking,
            use_container_width=True
        )