import streamlit as st


class KPICards:

    @staticmethod
    def show(engine):
        """Display KPI cards from analytics engine."""

        kpis = engine.get_kpis()

        # Row 1: General Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📋 Total Records", f"{kpis['total_records']:,}")

        with col2:
            st.metric("🚀 Average Speed", f"{kpis['average_speed']:.1f} km/h")

        with col3:
            st.metric("⏱ Average Travel Time", f"{kpis['average_travel_time']:.1f} min")

        with col4:
            st.metric("🛣 Active Corridors", kpis["active_routes"])

        st.markdown("##### 🚦 Peak Rush Hour Indicators (Weekdays 6-10 AM & 4-8 PM)")

        rush_idx = kpis.get("rush_hour_index_0_10", 0.0)
        extra_time_info = kpis.get("extra_time_per_50km", {})
        net_info = kpis.get("congested_network_pct", {})

        col_a, col_b, col_c, col_d = st.columns(4)

        with col_a:
            st.metric(
                "🔥 Rush Hour Congestion (0-10)",
                f"{rush_idx:.1f} / 10",
                delta=f"{'Heavy' if rush_idx >= 6 else 'Moderate' if rush_idx >= 3 else 'Low'} Impact",
                delta_color="inverse",
                help="Compare traffic during weekday rush hours (6-10AM & 4-8PM) to ideal free-flow environment (0=free flow, 10=gridlock)"
            )

        with col_b:
            extra_min = extra_time_info.get("extra_time_min", 0.0)
            st.metric(
                "⏳ Extra Time / 50 km",
                f"+{extra_min:.1f} min",
                delta=f"{extra_time_info.get('peak_time_min', 0.0):.1f} min total",
                delta_color="inverse",
                help="Extra travel time spent for 50 km travelled during peak hours compared to ideal free-flow speeds"
            )

        with col_c:
            pct = net_info.get("congested_pct", 0.0)
            st.metric(
                "📉 Congested Road Network",
                f"{pct:.1f}%",
                delta=f"{net_info.get('congested_length_km', 0.0):.1f} km of {net_info.get('total_network_km', 0.0):.1f} km",
                delta_color="inverse",
                help="Percentage of total road network length congested (speed < 25 km/h) at peak times"
            )

        with col_d:
            st.metric(
                "🚧 Congested Corridors",
                f"{net_info.get('congested_corridors_count', 0)} / {kpis['active_routes']}",
                delta=f"{net_info.get('congested_length_km', 0.0):.1f} km congested",
                delta_color="inverse",
                help="Number of corridors operating under heavy congestion speed threshold (<25 km/h) during peak times"
            )