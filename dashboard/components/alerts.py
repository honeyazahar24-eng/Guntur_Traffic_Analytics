import streamlit as st
import pandas as pd


class Alerts:

    @staticmethod
    def show(engine, threshold_speed=20.0):
        """Display traffic congestion alerts for corridors with average speed below threshold."""
        df = engine.get_dataframe()
        if df.empty:
            return

        recent_df = (
            df.groupby("corridor_id", as_index=False)
            .agg(
                Average_Speed=("average_speed_kmph", "mean"),
                Average_Time=("duration_seconds", "mean")
            )
        )

        congested = recent_df[recent_df["Average_Speed"] < threshold_speed]

        if not congested.empty:
            for _, row in congested.iterrows():
                corridor_id = int(row["corridor_id"])
                speed = row["Average_Speed"]
                time_min = row["Average_Time"] / 60
                st.error(
                    f"🚨 **Congestion Alert - Corridor {corridor_id}**: "
                    f"Average speed is low ({speed:.1f} km/h, travel time: {time_min:.1f} min)."
                )
        else:
            st.success("✅ All corridors are operating above critical congestion levels.")
