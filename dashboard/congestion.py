import pandas as pd
import numpy as np


class CongestionAnalyzer:
    """Utility class to calculate advanced congestion metrics and indices."""

    FREE_FLOW_SPEED = 45.0  # Ideal free-flow speed in km/h

    @staticmethod
    def filter_rush_hours(df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter dataframe for weekday rush hours:
        Mondays to Fridays, 6:00-10:00 AM (Hours 6-9) and 4:00-8:00 PM (Hours 16-19).
        """
        if df.empty:
            return df

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        rush_hours = [6, 7, 8, 9, 16, 17, 18, 19]

        return df[
            (df["day_name"].isin(weekdays)) &
            (df["hour"].isin(rush_hours))
        ]

    @staticmethod
    def calculate_congestion_index(df: pd.DataFrame, free_flow_speed: float = 45.0) -> pd.DataFrame:
        """
        Calculate Congestion Index = (Free Flow Speed - Average Speed) / Free Flow Speed.
        Value ranges from 0 (Free Flow) to 1 (Complete Gridlock).
        """
        if df.empty:
            return pd.DataFrame()

        result = df.groupby("corridor_id", as_index=False).agg(
            Average_Speed=("average_speed_kmph", "mean"),
            Average_Duration=("duration_seconds", "mean"),
            Distance_Km=("distance_km", "mean")
        )

        result["Congestion_Index"] = (
            (free_flow_speed - result["Average_Speed"]) / free_flow_speed
        ).clip(lower=0.0, upper=1.0).round(2)

        return result

    @staticmethod
    def rush_hour_congestion_scale_0_10(df: pd.DataFrame, free_flow_speed: float = 45.0) -> float:
        """
        Compare the flow of traffic during weekday rush hours (6-10AM and 4-8PM)
        to an ideal free-flow environment.
        Scale of 0 to 10 (0 = least congested, 10 = most congested).
        """
        rush_df = CongestionAnalyzer.filter_rush_hours(df)
        eval_df = rush_df if not rush_df.empty else df

        if eval_df.empty:
            return 0.0

        avg_speed = eval_df["average_speed_kmph"].mean()
        index_0_1 = (free_flow_speed - avg_speed) / free_flow_speed
        index_0_10 = max(0.0, min(10.0, index_0_1 * 10.0))
        return round(index_0_10, 1)

    @staticmethod
    def extra_time_per_50km(df: pd.DataFrame, free_flow_speed: float = 45.0) -> dict:
        """
        Calculate extra time spent driving per 50 km travelled during peak times
        (6-10AM & 4-8PM on weekdays) vs ideal free-flow travel time.
        Returns dict with peak_speed, free_flow_time_min, peak_time_min, extra_time_min.
        """
        rush_df = CongestionAnalyzer.filter_rush_hours(df)
        eval_df = rush_df if not rush_df.empty else df

        if eval_df.empty or eval_df["average_speed_kmph"].mean() == 0:
            return {
                "peak_speed_kmph": free_flow_speed,
                "free_flow_time_min": 66.7,
                "peak_time_min": 66.7,
                "extra_time_min": 0.0
            }

        peak_speed = eval_df["average_speed_kmph"].mean()
        free_flow_time_min = (50.0 / free_flow_speed) * 60.0  # 66.67 mins for 50km
        peak_time_min = (50.0 / peak_speed) * 60.0
        extra_time_min = max(0.0, peak_time_min - free_flow_time_min)

        return {
            "peak_speed_kmph": round(peak_speed, 1),
            "free_flow_time_min": round(free_flow_time_min, 1),
            "peak_time_min": round(peak_time_min, 1),
            "extra_time_min": round(extra_time_min, 1)
        }

    @staticmethod
    def congested_road_network_pct(df: pd.DataFrame, threshold_speed: float = 25.0) -> dict:
        """
        Calculate the percentage of roads congested at peak times (6-10AM and 4-8PM on weekdays).
        Calculated by comparing total length of congested roadway segments with total network length.
        A corridor is congested if peak hour avg speed < 25 km/h.
        """
        if df.empty:
            return {
                "total_network_km": 0.0,
                "congested_length_km": 0.0,
                "congested_pct": 0.0,
                "congested_corridors_count": 0
            }

        rush_df = CongestionAnalyzer.filter_rush_hours(df)
        eval_df = rush_df if not rush_df.empty else df

        # Get corridor-level peak stats
        corr_stats = eval_df.groupby("corridor_id", as_index=False).agg(
            Avg_Speed=("average_speed_kmph", "mean"),
            Length_Km=("distance_km", "mean")
        )

        total_length = corr_stats["Length_Km"].sum()
        congested_corrs = corr_stats[corr_stats["Avg_Speed"] < threshold_speed]
        congested_length = congested_corrs["Length_Km"].sum()
        congested_pct = (congested_length / total_length * 100.0) if total_length > 0 else 0.0

        return {
            "total_network_km": round(total_length, 2),
            "congested_length_km": round(congested_length, 2),
            "congested_pct": round(congested_pct, 1),
            "congested_corridors_count": len(congested_corrs)
        }

    @staticmethod
    def corridor_congestion_lengths(df: pd.DataFrame, threshold_speed: float = 25.0) -> pd.DataFrame:
        """
        Calculate congestion length and metrics for each individual corridor.
        """
        if df.empty:
            return pd.DataFrame()

        rush_df = CongestionAnalyzer.filter_rush_hours(df)
        eval_df = rush_df if not rush_df.empty else df

        summary = eval_df.groupby("corridor_id", as_index=False).agg(
            Origin=("origin_name", "first"),
            Destination=("destination_name", "first"),
            Corridor_Length_Km=("distance_km", "mean"),
            Peak_Speed_Kmph=("average_speed_kmph", "mean")
        )

        summary["Corridor_Length_Km"] = summary["Corridor_Length_Km"].round(2)
        summary["Peak_Speed_Kmph"] = summary["Peak_Speed_Kmph"].round(1)

        # Congestion Index 0-10 per corridor
        summary["Congestion_Scale_0_10"] = (
            (CongestionAnalyzer.FREE_FLOW_SPEED - summary["Peak_Speed_Kmph"]) / CongestionAnalyzer.FREE_FLOW_SPEED * 10.0
        ).clip(lower=0.0, upper=10.0).round(1)

        # Congested status & congested length (km)
        summary["Is_Congested"] = summary["Peak_Speed_Kmph"] < threshold_speed
        summary["Congested_Length_Km"] = summary.apply(
            lambda r: r["Corridor_Length_Km"] if r["Is_Congested"] else 0.0, axis=1
        )

        return summary.sort_values(by="Congestion_Scale_0_10", ascending=False)

