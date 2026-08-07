"""
Guntur Traffic Analytics Dashboard
Real-time traffic monitoring using Google Routes API data
"""

import sys
from pathlib import Path

file_path = Path(__file__).resolve()
project_root = file_path.parent.parent if file_path.parent.name == "dashboard" else file_path.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(file_path.parent) not in sys.path:
    sys.path.insert(0, str(file_path.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Local imports with robust fallback
try:
    from dashboard.data_loader import DataLoader
    from dashboard.analytics_engine import AnalyticsEngine
    from dashboard.filters import Filters
    from dashboard.components.header import Header
    from dashboard.components.kpi_cards import KPICards
    from dashboard.components.corridor_ranking import CorridorRanking
    from dashboard.components.traffic_status import TrafficStatus
    from dashboard.components.traffic_table import TrafficTable
    from dashboard.components.sidebar import Sidebar
    from dashboard.components.alerts import Alerts
    from dashboard.components.live_status import LiveStatus
    from dashboard.components.insights import InsightsComponent
    from dashboard.config import (
        APP_TITLE, PAGE_ICON, LAYOUT, INITIAL_SIDEBAR_STATE,
        CHART_HEIGHT, CHART_TEMPLATE, CHART_MARGIN,
        NORMAL_SPEED, MODERATE_SPEED,
        PRIMARY, SUCCESS, WARNING, DANGER, BACKGROUND
    )
    from dashboard.styles import Styles
    from dashboard.charts import (
        create_speed_trend_chart,
        create_travel_time_chart,
        create_corridor_performance_chart,
        create_hourly_speed_chart,
        create_hourly_travel_time_chart,
        create_daily_speed_chart,
        create_speed_heatmap,
    )
except ImportError:
    from data_loader import DataLoader
    from analytics_engine import AnalyticsEngine
    from filters import Filters
    from components.header import Header
    from components.kpi_cards import KPICards
    from components.corridor_ranking import CorridorRanking
    from components.traffic_status import TrafficStatus
    from components.traffic_table import TrafficTable
    from components.sidebar import Sidebar
    from components.alerts import Alerts
    from components.live_status import LiveStatus
    from components.insights import InsightsComponent
    from config import (
        APP_TITLE, PAGE_ICON, LAYOUT, INITIAL_SIDEBAR_STATE,
        CHART_HEIGHT, CHART_TEMPLATE, CHART_MARGIN,
        NORMAL_SPEED, MODERATE_SPEED,
        PRIMARY, SUCCESS, WARNING, DANGER, BACKGROUND
    )
    from styles import Styles
    from charts import (
        create_speed_trend_chart,
        create_travel_time_chart,
        create_corridor_performance_chart,
        create_hourly_speed_chart,
        create_hourly_travel_time_chart,
        create_daily_speed_chart,
        create_speed_heatmap,
    )



# ============================================================
# Background Collector Thread for Cloud Deployment (24/7)
# ============================================================
import threading
import schedule

if not getattr(sys, "_bg_scheduler_started", False):
    sys._bg_scheduler_started = True

    def _bg_collection_loop():
        try:
            from scripts.scheduler import run_collection
            schedule.every().hour.at(":00").do(run_collection)
            schedule.every().hour.at(":30").do(run_collection)
            while True:
                schedule.run_pending()
                time.sleep(5)
        except Exception:
            pass

    _t = threading.Thread(target=_bg_collection_loop, daemon=True)
    _t.start()



# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(

    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
)

Styles.load()


# ============================================================
# Auto-refresh logic
# ============================================================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

# Check for manual refresh
if st.session_state.get("manual_refresh", False):
    st.session_state.last_refresh = time.time()
    st.session_state.manual_refresh = False
    st.rerun()

# Auto-refresh every 5 minutes
if st.session_state.auto_refresh:
    if time.time() - st.session_state.last_refresh > 300:
        st.session_state.last_refresh = time.time()
        st.rerun()


# ============================================================
# Load Data
# ============================================================
@st.cache_data(ttl=60, show_spinner="Loading traffic data...")
def load_data():
    loader = DataLoader()
    return loader.load_data()


df = load_data()

if df.empty:
    st.warning("No traffic data found. Run the collector first: `python scripts/collector.py`")
    st.stop()


# ============================================================
# Sidebar Filters
# ============================================================
corridor, direction, date_range, refresh_clicked = Sidebar.show(df)

if refresh_clicked:
    st.session_state.manual_refresh = True
    st.rerun()

# Apply filters
filtered_df = df.copy()

if corridor != "All":
    filtered_df = filtered_df[filtered_df["corridor_id"] == corridor]

if direction != "All":
    filtered_df = filtered_df[filtered_df["direction"] == direction]

if date_range and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["collection_date"] >= str(start_date)) &
        (filtered_df["collection_date"] <= str(end_date))
    ]


# ============================================================
# Analytics Engine
# ============================================================
engine = AnalyticsEngine(filtered_df)


# ============================================================
# Header with KPIs
# ============================================================
Header.show(engine)


# ============================================================
# Main Dashboard Tabs
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "🚦 Corridor Analysis",
    "⏰ Time Patterns",
    "📊 Detailed Tables",
    "🗺️ Route Map"
])


# ============================================================
# TAB 1: OVERVIEW
# ============================================================
with tab1:
    st.subheader("Traffic Overview")

    # Display Alerts
    Alerts.show(engine)
    st.divider()

    # KPI Cards row
    KPICards.show(engine)

    st.divider()

    # Key Insights Section
    InsightsComponent.show(engine)

    st.divider()

    # Two-column layout for charts
    col1, col2 = st.columns(2)

    with col1:
        # Speed Trend Chart
        st.markdown("#### Speed Trend (Recent Collections)")
        speed_trend_fig = create_speed_trend_chart(filtered_df)
        st.plotly_chart(speed_trend_fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        # Travel Time Trend Chart
        st.markdown("#### Travel Time Trend (Recent Collections)")
        travel_time_fig = create_travel_time_chart(filtered_df)
        st.plotly_chart(travel_time_fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # Corridor Performance Bar Chart
    st.markdown("#### Average Speed by Corridor")
    corridor_perf_fig = create_corridor_performance_chart(filtered_df)
    st.plotly_chart(corridor_perf_fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # Traffic Status Summary
    st.markdown("#### Current Traffic Status by Corridor")
    TrafficStatus.show(engine)


# ============================================================
# TAB 2: CORRIDOR ANALYSIS
# ============================================================
with tab2:
    st.subheader("Corridor Deep Dive")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Corridor Ranking (Best → Worst Speed)")
        CorridorRanking.show(engine)

    with col2:
        st.markdown("#### Corridor Statistics")
        stats_df = engine.corridor_statistics()
        if not stats_df.empty:
            st.dataframe(
                stats_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "corridor_id": st.column_config.NumberColumn("Corridor ID", width="small"),
                    "Average_Speed": st.column_config.NumberColumn("Avg Speed (km/h)", format="%.1f"),
                    "Minimum_Speed": st.column_config.NumberColumn("Min Speed (km/h)", format="%.1f"),
                    "Maximum_Speed": st.column_config.NumberColumn("Max Speed (km/h)", format="%.1f"),
                    "Average_Travel_Time": st.column_config.NumberColumn("Avg Travel Time (min)", format="%.1f"),
                    "Total_Trips": st.column_config.NumberColumn("Trips", format="%d"),
                }
            )

    st.divider()

    # Peak Rush Hour Congestion & Length Breakdown
    st.markdown("#### 🔥 Weekday Peak Rush Hour Congestion & Length Analysis (6-10 AM & 4-8 PM)")
    st.caption("Measures traffic flow, 0-10 congestion scale, and congested road lengths during peak hours.")
    
    cong_len_df = engine.corridor_congestion_lengths()
    if not cong_len_df.empty:
        st.dataframe(
            cong_len_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "corridor_id": st.column_config.NumberColumn("Corridor ID", width="small"),
                "Origin": st.column_config.TextColumn("Origin"),
                "Destination": st.column_config.TextColumn("Destination"),
                "Corridor_Length_Km": st.column_config.NumberColumn("Corridor Length (km)", format="%.2f km"),
                "Free_Flow_Speed_Kmph": st.column_config.NumberColumn("Night Free-Flow Speed", format="%.1f km/h", help="Baseline speed measured from night-time (11 PM - 6 AM) collections"),
                "Peak_Speed_Kmph": st.column_config.NumberColumn("Peak Speed (km/h)", format="%.1f km/h"),
                "Congestion_Scale_0_10": st.column_config.ProgressColumn(
                    "Rush Hour Congestion (0-10)",
                    format="%.1f / 10",
                    min_value=0.0,
                    max_value=10.0,
                    help="0 = Free Flow, 10 = Severe Gridlock"
                ),
                "Is_Congested": st.column_config.CheckboxColumn("Congested? (<25 km/h)"),
                "Congested_Length_Km": st.column_config.NumberColumn("Congested Length (km)", format="%.2f km"),
            }
        )


    st.divider()

    # Direction comparison
    st.markdown("#### Direction Comparison")
    dir_summary = engine.direction_summary()
    if not dir_summary.empty:
        fig = px.bar(
            dir_summary,
            x="direction",
            y="Average_Speed",
            color="direction",
            text_auto=".1f",
            color_discrete_map={
                "Forward": PRIMARY,
                "Reverse": "#78909C"
            }
        )
        fig.update_layout(
            template=CHART_TEMPLATE,
            height=CHART_HEIGHT,
            margin=CHART_MARGIN,
            showlegend=False,
            xaxis_title=None,
            yaxis_title="Average Speed (km/h)"
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})



# ============================================================
# TAB 3: TIME PATTERNS
# ============================================================
with tab3:
    st.subheader("Temporal Patterns")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Average Speed by Hour of Day")
        hourly_fig = create_hourly_speed_chart(filtered_df)
        st.plotly_chart(hourly_fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown("#### Average Travel Time by Hour")
        hourly_time_fig = create_hourly_travel_time_chart(filtered_df)
        st.plotly_chart(hourly_time_fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # Daily trend
    st.markdown("#### Daily Average Speed Trend")
    daily_fig = create_daily_speed_chart(filtered_df)
    st.plotly_chart(daily_fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # Heatmap: Hour vs Corridor
    st.markdown("#### Speed Heatmap: Hour × Corridor")
    heatmap_fig = create_speed_heatmap(filtered_df)
    st.plotly_chart(heatmap_fig, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# TAB 4: DETAILED TABLES
# ============================================================
with tab4:
    st.subheader("Detailed Data Tables")

    # Latest Records
    st.markdown("#### Latest Traffic Records")
    TrafficTable.show_latest(engine)

    st.divider()

    # Full filtered data
    st.markdown("#### All Filtered Records")
    st.dataframe(
        filtered_df.sort_values(
            ["collection_date", "collection_time"],
            ascending=False
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "collection_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "collection_time": st.column_config.TimeColumn("Time", format="HH:mm:ss"),
            "day_name": st.column_config.TextColumn("Day"),
            "hour": st.column_config.NumberColumn("Hour", width="small"),
            "corridor_id": st.column_config.NumberColumn("Corridor", width="small"),
            "direction": st.column_config.TextColumn("Direction"),
            "origin_name": st.column_config.TextColumn("Origin"),
            "destination_name": st.column_config.TextColumn("Destination"),
            "distance_km": st.column_config.NumberColumn("Distance (km)", format="%.2f"),
            "duration_seconds": st.column_config.NumberColumn("Duration (sec)", format="%d"),
            "average_speed_kmph": st.column_config.NumberColumn("Avg Speed (km/h)", format="%.1f"),
        }
    )

    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f"guntur_traffic_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# TAB 5: ROUTE MAP
# ============================================================
with tab5:
    st.subheader("Route Network Map")

    from utils.route_manager import RouteManager
    from dashboard.map_view import MapView

    rm = RouteManager()
    routes_df = rm.load_routes()

    st.markdown("#### Defined Corridors")
    st.dataframe(
        routes_df[["Corridor_ID", "Direction", "Origin_Name", "Destination_Name", "Origin_Lat", "Origin_Lng", "Destination_Lat", "Destination_Lng"]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.markdown("#### View Corridor Map")

    col_a, col_b = st.columns(2)
    with col_a:
        selected_corridor = st.selectbox(
            "Select Corridor",
            options=sorted(routes_df["Corridor_ID"].unique().tolist()),
            format_func=lambda x: f"Corridor {x}"
        )
    with col_b:
        selected_direction = st.selectbox(
            "Select Direction",
            options=["Forward", "Reverse"]
        )

    MapView.show_corridor_map(selected_corridor, selected_direction)


# ============================================================
# Footer
# ============================================================
st.divider()
st.caption(
    f"🚦 {APP_TITLE} | "
    f"Last updated: {engine.latest_timestamp()} | "
    f"Data source: Google Routes API (Compute Routes) | "
    f"Auto-refresh: {'ON' if st.session_state.auto_refresh else 'OFF'} (5 min)"
)
