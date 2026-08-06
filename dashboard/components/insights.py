import streamlit as st
import pandas as pd


class InsightsComponent:

    @staticmethod
    def show(engine):
        """Display key insights generated from the traffic analytics engine."""
        df = engine.get_dataframe()
        if df.empty:
            st.info("No data available to generate insights.")
            return

        ranking = engine.corridor_ranking()
        if not ranking.empty:
            best = ranking.iloc[0]
            worst = ranking.iloc[-1]

            st.markdown("### 💡 Key Analytics Insights")
            st.markdown(
                f"- **Fastest Corridor**: Corridor **{int(best['corridor_id'])}** "
                f"with an average speed of **{best['Average_Speed']:.1f} km/h**."
            )
            st.markdown(
                f"- **Slowest Corridor**: Corridor **{int(worst['corridor_id'])}** "
                f"with an average speed of **{worst['Average_Speed']:.1f} km/h**."
            )

        hourly = engine.hourly_summary()
        if not hourly.empty:
            peak_hour_row = hourly.loc[hourly["Average_Travel_Time"].idxmax()]
            st.markdown(
                f"- **Peak Delay Hour**: **{int(peak_hour_row['hour'])}:00** "
                f"with average travel time of **{peak_hour_row['Average_Travel_Time']:.1f} minutes**."
            )
