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

    NIGHT_HOURS = [23, 0, 1, 2, 3, 4, 5]  # 11:00 PM to 6:00 AM

    @staticmethod
    def get_per_corridor_free_flow_speeds(df: pd.DataFrame) -> pd.Series:
        """
        Calculate dynamic per-corridor free-flow speeds from night hours (11 PM - 6 AM).
        If night-time data is not yet collected for a corridor, fallback to off-peak baseline.
        """
        if df.empty:
            return pd.Series(dtype=float)

        night_df = df[df["hour"].isin(CongestionAnalyzer.NIGHT_HOURS)]
        if not night_df.empty:
            night_speeds = night_df.groupby("corridor_id")["average_speed_kmph"].mean()
        else:
            night_speeds = pd.Series(dtype=float)

        all_corridors = sorted(df["corridor_id"].unique())
        free_flow_dict = {}
        for cid in all_corridors:
            if cid in night_speeds.index and not pd.isna(night_speeds[cid]):
                free_flow_dict[cid] = float(night_speeds[cid])
            else:
                corr_speeds = df[df["corridor_id"] == cid]["average_speed_kmph"]
                if not corr_speeds.empty:
                    q90 = corr_speeds.quantile(0.90) * 1.2
                    free_flow_dict[cid] = min(50.0, max(25.0, q90))
                else:
                    free_flow_dict[cid] = CongestionAnalyzer.FREE_FLOW_SPEED

        return pd.Series(free_flow_dict)

    @staticmethod
    def rush_hour_congestion_scale_0_10(df: pd.DataFrame, free_flow_speed: float = 45.0) -> float:
        """
        Compare the flow of traffic during weekday rush hours (6-10AM and 4-8PM)
        to per-corridor night-time free-flow speeds.
        Scale of 0 to 10 (0 = least congested, 10 = most congested).
        """
        rush_df = CongestionAnalyzer.filter_rush_hours(df)
        eval_df = rush_df if not rush_df.empty else df

        if eval_df.empty:
            return 0.0

        ff_speeds = CongestionAnalyzer.get_per_corridor_free_flow_speeds(df)
        eval_corr_speeds = eval_df.groupby("corridor_id")["average_speed_kmph"].mean()

        ratios = []
        for cid, avg_spd in eval_corr_speeds.items():
            ff_spd = ff_speeds.get(cid, free_flow_speed)
            ratio = max(0.0, min(1.0, (ff_spd - avg_spd) / ff_spd))
            ratios.append(ratio)

        avg_ratio = float(np.mean(ratios)) if ratios else 0.0
        return round(avg_ratio * 10.0, 1)

    @staticmethod
    def extra_time_per_50km(df: pd.DataFrame, free_flow_speed: float = 45.0) -> dict:
        """
        Calculate extra time spent driving per 50 km travelled during peak times
        (6-10AM & 4-8PM on weekdays) vs per-corridor night-time free-flow speeds.
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

        ff_speeds = CongestionAnalyzer.get_per_corridor_free_flow_speeds(df)
        avg_ff_speed = float(ff_speeds.mean()) if not ff_speeds.empty else free_flow_speed
        peak_speed = eval_df["average_speed_kmph"].mean()

        free_flow_time_min = (50.0 / avg_ff_speed) * 60.0
        peak_time_min = (50.0 / peak_speed) * 60.0
        extra_time_min = max(0.0, peak_time_min - free_flow_time_min)

        return {
            "peak_speed_kmph": round(peak_speed, 1),
            "free_flow_time_min": round(free_flow_time_min, 1),
            "peak_time_min": round(peak_time_min, 1),
            "extra_time_min": round(extra_time_min, 1)
        }

    @staticmethod
    def get_corridor_master_lengths(df: pd.DataFrame) -> pd.DataFrame:
        """
        Get the latest accurate corridor lengths (averaged over latest forward/reverse directions).
        """
        if df.empty:
            return pd.DataFrame()
        latest_by_dir = df.sort_values(["collection_date", "collection_time"]).groupby(["corridor_id", "direction"], as_index=False).agg(
            Origin=("origin_name", "last"),
            Destination=("destination_name", "last"),
            Distance_Km=("distance_km", "last")
        )
        corrs = latest_by_dir.groupby("corridor_id", as_index=False).agg(
            Origin=("Origin", "first"),
            Destination=("Destination", "first"),
            Corridor_Length_Km=("Distance_Km", "mean")
        )
        corrs["Corridor_Length_Km"] = corrs["Corridor_Length_Km"].round(2)
        return corrs

    @staticmethod
    def congested_road_network_pct(df: pd.DataFrame, threshold_speed: float = 25.0) -> dict:
        """
        Calculate the percentage of roads congested at peak times (6-10AM and 4-8PM on weekdays).
        Calculated by comparing total length of congested roadway segments with total network length.
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

        master_lens = CongestionAnalyzer.get_corridor_master_lengths(df)
        if master_lens.empty:
            return {
                "total_network_km": 0.0,
                "congested_length_km": 0.0,
                "congested_pct": 0.0,
                "congested_corridors_count": 0
            }

        peak_speeds = eval_df.groupby("corridor_id", as_index=False).agg(
            Avg_Speed=("average_speed_kmph", "mean")
        )

        corr_stats = master_lens.merge(peak_speeds, on="corridor_id", how="left")
        corr_stats["Avg_Speed"] = corr_stats["Avg_Speed"].fillna(CongestionAnalyzer.FREE_FLOW_SPEED)

        total_length = corr_stats["Corridor_Length_Km"].sum()
        congested_corrs = corr_stats[corr_stats["Avg_Speed"] < threshold_speed]
        congested_length = congested_corrs["Corridor_Length_Km"].sum()
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
        Uses dynamic per-corridor night-time (11 PM - 6 AM) free-flow speeds.
        """
        if df.empty:
            return pd.DataFrame()

        rush_df = CongestionAnalyzer.filter_rush_hours(df)
        eval_df = rush_df if not rush_df.empty else df

        master_lens = CongestionAnalyzer.get_corridor_master_lengths(df)
        if master_lens.empty:
            return pd.DataFrame()

        peak_speeds = eval_df.groupby("corridor_id", as_index=False).agg(
            Peak_Speed_Kmph=("average_speed_kmph", "mean")
        )

        summary = master_lens.merge(peak_speeds, on="corridor_id", how="left")
        summary["Peak_Speed_Kmph"] = summary["Peak_Speed_Kmph"].fillna(CongestionAnalyzer.FREE_FLOW_SPEED).round(1)

        ff_speeds = CongestionAnalyzer.get_per_corridor_free_flow_speeds(df)
        summary["Free_Flow_Speed_Kmph"] = summary["corridor_id"].map(ff_speeds).round(1)

        summary["Congestion_Ratio"] = (
            (summary["Free_Flow_Speed_Kmph"] - summary["Peak_Speed_Kmph"]) / summary["Free_Flow_Speed_Kmph"]
        ).clip(lower=0.0, upper=1.0)

        summary["Congestion_Scale_0_10"] = (summary["Congestion_Ratio"] * 10.0).round(1)
        summary["Congested_Length_Km"] = (summary["Corridor_Length_Km"] * summary["Congestion_Ratio"]).round(2)
        summary["Is_Congested"] = summary["Peak_Speed_Kmph"] < threshold_speed

        drop_cols = ["Congestion_Ratio"]
        return summary.drop(columns=drop_cols).sort_values(by="Congestion_Scale_0_10", ascending=False)




