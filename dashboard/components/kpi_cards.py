import streamlit as st


class KPICards:

    @staticmethod
    def show(engine):
        """Display KPI cards from analytics engine."""

        kpis = engine.get_kpis()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📋 Total Records",
                f"{kpis['total_records']:,}"
            )

        with col2:
            st.metric(
                "🚀 Average Speed",
                f"{kpis['average_speed']:.1f} km/h"
            )

        with col3:
            st.metric(
                "⏱ Average Travel Time",
                f"{kpis['average_travel_time']:.1f} min"
            )

        with col4:
            st.metric(
                "🛣 Active Corridors",
                kpis["active_routes"]
            )