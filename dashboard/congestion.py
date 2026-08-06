import pandas as pd


class CongestionAnalyzer:
    """Utility class to calculate congestion metrics and indices."""

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
            Average_Duration=("duration_seconds", "mean")
        )

        result["Congestion_Index"] = (
            (free_flow_speed - result["Average_Speed"]) / free_flow_speed
        ).clip(lower=0.0, upper=1.0).round(2)

        return result
