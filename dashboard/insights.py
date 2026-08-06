import pandas as pd


class TrafficInsightsEngine:
    """Analytical insights generator for traffic dataset."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_summary_insights(self) -> dict:
        if self.df.empty:
            return {"status": "No data available"}

        avg_speed = self.df["average_speed_kmph"].mean()
        busiest_hour = self.df.groupby("hour")["duration_seconds"].mean().idxmax()
        slowest_corridor = self.df.groupby("corridor_id")["average_speed_kmph"].mean().idxmin()

        return {
            "overall_average_speed": round(avg_speed, 2),
            "peak_congestion_hour": int(busiest_hour),
            "slowest_corridor": int(slowest_corridor),
            "total_observations": len(self.df)
        }
