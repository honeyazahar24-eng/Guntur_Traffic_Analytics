import streamlit as st


class Header:

    @staticmethod
    def show(engine):

        st.title("🚦 Guntur Traffic Analytics Platform")
        st.caption("Real-Time Traffic Monitoring")

        st.write(
            f"**Last Updated:** {engine.latest_timestamp()}"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Routes",
            engine.active_routes()
        )

        c2.metric(
            "Records",
            f"{engine.total_records():,}"
        )

        c3.metric(
            "Average Speed",
            f"{engine.average_speed()} km/h"
        )

        c4.metric(
            "Travel Time",
            f"{engine.average_travel_time()} min"
        )

        st.divider()