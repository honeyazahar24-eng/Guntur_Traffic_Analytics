import streamlit as st
import pandas as pd


class LiveStatus:

    @staticmethod
    def show(engine):
        """Display real-time traffic status cards."""
        status_df = engine.traffic_status()

        if status_df.empty:
            st.info("No live status data available.")
            return

        cols = st.columns(min(len(status_df), 4))
        for idx, (_, row) in enumerate(status_df.iterrows()):
            col = cols[idx % 4]
            corridor_id = int(row["corridor_id"])
            speed = row["Average_Speed"]
            status = row["Traffic_Status"]
            col.metric(
                label=f"Corridor {corridor_id}",
                value=f"{speed:.1f} km/h",
                delta=status
            )
