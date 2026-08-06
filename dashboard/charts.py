import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.config import (
    CHART_HEIGHT,
    CHART_MARGIN,
    CHART_TEMPLATE,
    NORMAL_SPEED,
    MODERATE_SPEED,
    PRIMARY,
    SUCCESS,
    WARNING,
    DANGER
)


def empty_chart(title: str) -> go.Figure:
    """Create empty chart placeholder."""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        height=CHART_HEIGHT,
        margin=CHART_MARGIN,
        annotations=[dict(
            text="No Data Available",
            showarrow=False,
            x=0.5, y=0.5,
            font=dict(size=16, color="#999")
        )]
    )
    return fig


def apply_layout(fig: go.Figure, title: str, yaxis_title: str) -> go.Figure:
    """Apply consistent layout to all charts."""
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        template=CHART_TEMPLATE,
        height=CHART_HEIGHT,
        margin=CHART_MARGIN,
        hovermode="x unified",
        legend_title=None,
        xaxis_title=None,
        yaxis_title=yaxis_title,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E1E0D9",
            gridwidth=1,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E1E0D9",
            gridwidth=1,
            zeroline=False
        )
    )
    return fig


def create_speed_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Create speed trend line chart with proper styling."""
    if df.empty:
        return empty_chart("Average Speed Trend")

    chart_df = df.copy()
    chart_df["timestamp"] = pd.to_datetime(
        chart_df["collection_date"].astype(str) + " " + chart_df["collection_time"].astype(str)
    )
    chart_df = chart_df.sort_values("timestamp")

    agg_df = chart_df.groupby("timestamp", as_index=False).agg(
        Average_Speed=("average_speed_kmph", "mean")
    )

    fig = px.line(
        agg_df,
        x="timestamp",
        y="Average_Speed",
        markers=True,
        line_shape="spline"
    )

    fig.update_traces(
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=6, color=PRIMARY, line=dict(width=2, color="white")),
        hovertemplate="<b>%{y:.1f} km/h</b><br>%{x}<extra></extra>"
    )

    fig.add_hline(y=NORMAL_SPEED, line_dash="dot", line_color=SUCCESS, line_width=1,
                  annotation_text="Normal (≥40)", annotation_position="bottom right")
    fig.add_hline(y=MODERATE_SPEED, line_dash="dot", line_color=WARNING, line_width=1,
                  annotation_text="Moderate (≥25)", annotation_position="bottom right")

    return apply_layout(fig, "Average Speed Trend", "Speed (km/h)")


def create_travel_time_chart(df: pd.DataFrame) -> go.Figure:
    """Create travel time trend line chart."""
    if df.empty:
        return empty_chart("Travel Time Trend")

    chart_df = df.copy()
    chart_df["timestamp"] = pd.to_datetime(
        chart_df["collection_date"].astype(str) + " " + chart_df["collection_time"].astype(str)
    )
    chart_df = chart_df.sort_values("timestamp")
    chart_df["travel_minutes"] = chart_df["duration_seconds"] / 60

    agg_df = chart_df.groupby("timestamp", as_index=False).agg(
        Average_Travel_Time=("travel_minutes", "mean")
    )

    fig = px.line(
        agg_df,
        x="timestamp",
        y="Average_Travel_Time",
        markers=True,
        line_shape="spline"
    )

    fig.update_traces(
        line=dict(color=WARNING, width=3),
        marker=dict(size=6, color=WARNING, line=dict(width=2, color="white")),
        hovertemplate="<b>%{y:.1f} min</b><br>%{x}<extra></extra>"
    )

    return apply_layout(fig, "Travel Time Trend", "Travel Time (Minutes)")


def create_corridor_performance_chart(df: pd.DataFrame) -> go.Figure:
    """Create horizontal bar chart for corridor performance."""
    if df.empty:
        return empty_chart("Corridor Performance")

    chart_df = (
        df.groupby("corridor_id", as_index=False)
        .agg(Average_Speed=("average_speed_kmph", "mean"))
        .sort_values("Average_Speed", ascending=True)
    )

    colors = []
    for speed in chart_df["Average_Speed"]:
        if speed >= NORMAL_SPEED:
            colors.append(SUCCESS)
        elif speed >= MODERATE_SPEED:
            colors.append(WARNING)
        else:
            colors.append(DANGER)

    fig = go.Figure(go.Bar(
        x=chart_df["Average_Speed"],
        y=[f"Corridor {int(c)}" for c in chart_df["corridor_id"]],
        orientation="h",
        marker_color=colors,
        text=chart_df["Average_Speed"].round(1),
        textposition="outside",
        hovertemplate="Corridor %{y}<br><b>%{x:.1f} km/h</b><extra></extra>"
    ))

    fig.add_vline(x=NORMAL_SPEED, line_dash="dot", line_color=SUCCESS, line_width=1)
    fig.add_vline(x=MODERATE_SPEED, line_dash="dot", line_color=WARNING, line_width=1)

    return apply_layout(fig, "Average Speed by Corridor", "Speed (km/h)")


def create_hourly_speed_chart(df: pd.DataFrame) -> go.Figure:
    """Create hourly average speed bar chart."""
    if df.empty:
        return empty_chart("Hourly Speed")

    chart_df = (
        df.groupby("hour", as_index=False)
        .agg(Average_Speed=("average_speed_kmph", "mean"))
        .sort_values("hour")
    )

    all_hours = pd.DataFrame({"hour": range(24)})
    chart_df = all_hours.merge(chart_df, on="hour", how="left")

    colors = []
    for speed in chart_df["Average_Speed"]:
        if pd.isna(speed):
            colors.append("#E0E0E0")
        elif speed >= NORMAL_SPEED:
            colors.append(SUCCESS)
        elif speed >= MODERATE_SPEED:
            colors.append(WARNING)
        else:
            colors.append(DANGER)

    fig = go.Figure(go.Bar(
        x=chart_df["hour"],
        y=chart_df["Average_Speed"],
        marker_color=colors,
        text=chart_df["Average_Speed"].round(1),
        textposition="outside",
        hovertemplate="Hour %{x}:00<br><b>%{y:.1f} km/h</b><extra></extra>"
    ))

    fig.update_xaxes(
        tickmode="linear",
        tick0=0,
        dtick=2,
        range=[-0.5, 23.5]
    )

    fig.add_hline(y=NORMAL_SPEED, line_dash="dot", line_color=SUCCESS, line_width=1)
    fig.add_hline(y=MODERATE_SPEED, line_dash="dot", line_color=WARNING, line_width=1)

    return apply_layout(fig, "Average Speed by Hour", "Speed (km/h)")


def create_hourly_travel_time_chart(df: pd.DataFrame) -> go.Figure:
    """Create hourly average travel time bar chart."""
    if df.empty:
        return empty_chart("Hourly Travel Time")

    chart_df = (
        df.groupby("hour", as_index=False)
        .agg(Average_Travel_Time=("duration_seconds", "mean"))
        .sort_values("hour")
    )
    chart_df["Average_Travel_Time"] = chart_df["Average_Travel_Time"] / 60

    all_hours = pd.DataFrame({"hour": range(24)})
    chart_df = all_hours.merge(chart_df, on="hour", how="left")

    fig = go.Figure(go.Bar(
        x=chart_df["hour"],
        y=chart_df["Average_Travel_Time"],
        marker_color=PRIMARY,
        text=chart_df["Average_Travel_Time"].round(1),
        textposition="outside",
        hovertemplate="Hour %{x}:00<br><b>%{y:.1f} min</b><extra></extra>"
    ))

    fig.update_xaxes(
        tickmode="linear",
        tick0=0,
        dtick=2,
        range=[-0.5, 23.5]
    )

    return apply_layout(fig, "Average Travel Time by Hour", "Travel Time (Minutes)")


def create_daily_speed_chart(df: pd.DataFrame) -> go.Figure:
    """Create daily average speed trend line chart."""
    if df.empty:
        return empty_chart("Daily Average Speed")

    chart_df = (
        df.groupby("collection_date", as_index=False)
        .agg(Average_Speed=("average_speed_kmph", "mean"))
        .sort_values("collection_date")
    )
    chart_df["collection_date"] = pd.to_datetime(chart_df["collection_date"])

    fig = px.line(
        chart_df,
        x="collection_date",
        y="Average_Speed",
        markers=True,
        line_shape="spline"
    )

    fig.update_traces(
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=8, color=PRIMARY, line=dict(width=2, color="white")),
        hovertemplate="<b>%{y:.1f} km/h</b><br>%{x|%Y-%m-%d}<extra></extra>"
    )

    fig.add_hline(y=NORMAL_SPEED, line_dash="dot", line_color=SUCCESS, line_width=1)
    fig.add_hline(y=MODERATE_SPEED, line_dash="dot", line_color=WARNING, line_width=1)

    fig.update_xaxes(
        tickformat="%b %d",
        showgrid=False
    )

    return apply_layout(fig, "Daily Average Speed Trend", "Speed (km/h)")


def create_speed_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create heatmap of speed by hour and corridor."""
    if df.empty:
        return empty_chart("Speed Heatmap: Hour × Corridor")

    pivot = df.pivot_table(
        values="average_speed_kmph",
        index="corridor_id",
        columns="hour",
        aggfunc="mean"
    )

    for h in range(24):
        if h not in pivot.columns:
            pivot[h] = None
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)

    for c in range(1, 11):
        if c not in pivot.index:
            pivot.loc[c] = None
    pivot = pivot.sort_index()

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"{h}:00" for h in pivot.columns],
        y=[f"Corridor {int(i)}" for i in pivot.index],
        colorscale="RdYlGn",
        zmin=0,
        zmax=50,
        text=[[f"{v:.1f}" if pd.notna(v) else "" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate="Corridor %{y}<br>Hour %{x}<br><b>%{z:.1f} km/h</b><extra></extra>",
        colorbar=dict(title="Speed (km/h)", thickness=15, len=0.75)
    ))

    fig.update_layout(
        template=CHART_TEMPLATE,
        height=500,
        margin=CHART_MARGIN,
        xaxis=dict(side="top", tickangle=-45),
        yaxis=dict(autorange="reversed")
    )

    return fig


class Charts:
    """Class wrapper for charts for backward compatibility."""
    @staticmethod
    def speed_trend(df):
        return create_speed_trend_chart(df)

    @staticmethod
    def corridor_performance(df):
        return create_corridor_performance_chart(df)

    @staticmethod
    def hourly_speed(df):
        return create_hourly_speed_chart(df)

    @staticmethod
    def travel_time_trend(df):
        return create_travel_time_chart(df)

    @staticmethod
    def daily_speed(df):
        return create_daily_speed_chart(df)