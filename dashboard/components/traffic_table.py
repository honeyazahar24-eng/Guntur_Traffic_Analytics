import streamlit as st


class TrafficTable:

    @staticmethod
    def show_latest(engine, limit=20):
        """Display latest traffic records from engine."""

        st.markdown("#### Latest Traffic Observations")

        df = engine.get_latest_records(limit)

        if df.empty:
            st.info("No records to display")
            return

        display_df = df.copy()

        display_df["Travel Time (min)"] = (
            display_df["duration_seconds"] / 60
        ).round(2)

        display_df["Average Speed (km/h)"] = (
            display_df["average_speed_kmph"]
        ).round(2)

        columns = [
            "collection_date",
            "collection_time",
            "corridor_id",
            "direction",
            "origin_name",
            "destination_name",
            "Average Speed (km/h)",
            "Travel Time (min)"
        ]

        display_df = display_df[columns]

        display_df.columns = [
            "Date",
            "Time (IST)",
            "Corridor",

            "Direction",
            "Origin",
            "Destination",
            "Speed (km/h)",
            "Travel Time (min)"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )