import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date, timedelta


class Sidebar:

    @staticmethod
    def show(df):

        st.sidebar.title("🚦 Traffic Analytics")

        st.sidebar.markdown("---")

        # ======================================================
        # Live Scheduler Status
        # ======================================================
        st.sidebar.subheader("📡 Live Collector Status")
        status_file = Path(__file__).resolve().parent.parent.parent / "logs" / "scheduler_status.json"
        
        if status_file.exists():
            try:
                with open(status_file, "r") as f:
                    sched_info = json.load(f)
                
                status = sched_info.get("status", "unknown")
                if status == "success":
                    st.sidebar.success(f"🟢 Active — Last run: {sched_info.get('last_run', 'N/A')}")
                elif status == "running":
                    st.sidebar.info("⏳ Data Collection in Progress...")
                elif status == "error":
                    st.sidebar.error("🔴 Collector Error — Check logs")
                else:
                    st.sidebar.warning("⚪ Scheduler Status Unknown")

                st.sidebar.caption(f"⏰ **Next auto-collect:** {sched_info.get('next_run', 'Every 30 min (:00 & :30)')}")
            except Exception:
                st.sidebar.caption("⏰ Auto-collect: Every 30 min (:00 & :30)")
        else:
            st.sidebar.caption("⏰ Auto-collect: Every 30 min (:00 & :30)")

        collect_now = st.sidebar.button(
            "⚡ Collect Data Now",
            use_container_width=True,
            help="Trigger an immediate Google Routes API traffic collection"
        )
        if collect_now:
            with st.sidebar.status("Fetching live traffic data from Google API..."):
                try:
                    from scripts.collector import main as collect_main
                    collect_main()
                    st.sidebar.success("✅ Traffic data updated successfully!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"❌ Collection failed: {e}")

        st.sidebar.markdown("---")

        st.sidebar.subheader("📊 Filters")

        # ======================================================
        # Date Range Filter
        # ======================================================

        date_range = None
        if "collection_date" in df.columns:
            df_dates = pd.to_datetime(df["collection_date"], errors="coerce").dropna()
            if len(df_dates) > 0:
                min_date = df_dates.min().date()
                max_date = df_dates.max().date()

                date_range = st.sidebar.date_input(
                    "Date Range",
                    value=(max_date - timedelta(days=7), max_date),
                    min_value=min_date,
                    max_value=max_date,
                    help="Select date range for analysis"
                )

        # ======================================================
        # Corridor Filter
        # ======================================================

        corridor = "All"
        if "corridor_id" in df.columns:
            corridors = sorted(df["corridor_id"].dropna().unique().astype(int).tolist())
            corridor_options = ["All"] + corridors
            corridor = st.sidebar.selectbox(
                "Corridor",
                options=corridor_options,
                index=0,
                help="Filter by specific corridor"
            )

        # ======================================================
        # Direction Filter
        # ======================================================

        direction = "All"
        if "direction" in df.columns:
            directions = sorted(df["direction"].dropna().unique().tolist())
            direction = st.sidebar.selectbox(
                "Direction",
                options=["All"] + directions,
                index=0,
                help="Filter by travel direction"
            )

        st.sidebar.markdown("---")

        # ======================================================
        # Refresh Button
        # ======================================================

        refresh_clicked = st.sidebar.button(
            "🔄 Refresh Dashboard",
            use_container_width=True,
            type="primary",
            help="Force refresh data from database"
        )

        st.sidebar.markdown("---")

        # ======================================================
        # Auto-refresh Toggle
        # ======================================================

        auto_refresh = st.sidebar.checkbox(
            "⚡ Auto-refresh Dashboard (5 min)",
            value=st.session_state.get("auto_refresh", True),
            help="Automatically refresh dashboard data every 5 minutes"
        )
        st.session_state.auto_refresh = auto_refresh

        st.sidebar.markdown("---")

        # ======================================================
        # Summary Stats
        # ======================================================

        st.sidebar.subheader("📈 Summary")

        # Apply filters to compute summary
        summary_df = df.copy()
        if corridor != "All":
            summary_df = summary_df[summary_df["corridor_id"] == corridor]
        if direction != "All":
            summary_df = summary_df[summary_df["direction"] == direction]
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            summary_df = summary_df[
                (pd.to_datetime(summary_df["collection_date"]).dt.date >= start_date) &
                (pd.to_datetime(summary_df["collection_date"]).dt.date <= end_date)
            ]

        st.sidebar.metric("Corridors", summary_df["corridor_id"].nunique() if len(summary_df) > 0 else 0)
        st.sidebar.metric("Records", len(summary_df))

        if len(summary_df) > 0:
            st.sidebar.metric("Avg Speed", f"{summary_df['average_speed_kmph'].mean():.1f} km/h")
            st.sidebar.metric("Avg Time", f"{summary_df['duration_seconds'].mean()/60:.1f} min")

        return corridor, direction, date_range, refresh_clicked