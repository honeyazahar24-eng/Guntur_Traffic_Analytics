import pandas as pd


class AnalyticsEngine:

    def __init__(self, df):
        self.df = df.copy()

    # ==========================================================
    # Data
    # ==========================================================

    def get_dataframe(self):
        return self.df

    # ==========================================================
    # Basic KPIs
    # ==========================================================

    def total_records(self):
        return len(self.df)

    def total_routes(self):
        if self.df.empty:
            return 0
        return self.df["corridor_id"].nunique()

    def active_routes(self):
        return self.total_routes()

    def average_speed(self):
        if self.df.empty:
            return 0.0

        return round(
            self.df["average_speed_kmph"].mean(),
            2
        )

    def average_travel_time(self):
        if self.df.empty:
            return 0.0

        return round(
            self.df["duration_seconds"].mean() / 60,
            2
        )

    def latest_date(self):

        if self.df.empty:
            return "-"

        return str(
            self.df["collection_date"].max()
        )

    def latest_timestamp(self):

        if self.df.empty:
            return "-"

        latest = (
            self.df
            .sort_values(
                ["collection_date", "collection_time"]
            )
            .iloc[-1]
        )

        return (
            f"{latest['collection_date']} "
            f"{latest['collection_time']}"
        )

    # ==========================================================
    # Peak Rush Hour Congestion Metrics
    # ==========================================================

    def rush_hour_congestion_index_0_10(self):
        from dashboard.congestion import CongestionAnalyzer
        return CongestionAnalyzer.rush_hour_congestion_scale_0_10(self.df)

    def extra_time_per_50km(self):
        from dashboard.congestion import CongestionAnalyzer
        return CongestionAnalyzer.extra_time_per_50km(self.df)

    def congested_road_network_pct(self):
        from dashboard.congestion import CongestionAnalyzer
        return CongestionAnalyzer.congested_road_network_pct(self.df)

    def corridor_congestion_lengths(self):
        from dashboard.congestion import CongestionAnalyzer
        return CongestionAnalyzer.corridor_congestion_lengths(self.df)

    # ==========================================================
    # KPI Dictionary
    # ==========================================================

    def get_kpis(self):

        return {

            "total_records": self.total_records(),

            "average_speed": self.average_speed(),

            "average_travel_time": self.average_travel_time(),

            "latest_date": self.latest_date(),

            "active_routes": self.active_routes(),

            "rush_hour_index_0_10": self.rush_hour_congestion_index_0_10(),

            "extra_time_per_50km": self.extra_time_per_50km(),

            "congested_network_pct": self.congested_road_network_pct(),

        }


    # ==========================================================
    # Latest Records
    # ==========================================================

    def get_latest_records(self, limit=20):

        if self.df.empty:
            return self.df

        return (
            self.df
            .sort_values(
                by=[
                    "collection_date",
                    "collection_time"
                ],
                ascending=False
            )
            .head(limit)
        )

    # ==========================================================
    # Corridor Ranking
    # ==========================================================

    def corridor_ranking(self):

        if self.df.empty:
            return pd.DataFrame()

        ranking = (

            self.df

            .groupby(
                "corridor_id",
                as_index=False
            )

            .agg(

                Average_Speed=(
                    "average_speed_kmph",
                    "mean"
                ),

                Average_Travel_Time=(
                    "duration_seconds",
                    "mean"
                ),

                Total_Trips=(
                    "corridor_id",
                    "count"
                )

            )

        )

        ranking["Average_Speed"] = (
            ranking["Average_Speed"]
            .round(2)
        )

        ranking["Average_Travel_Time"] = (
            ranking["Average_Travel_Time"] / 60
        ).round(2)

        ranking = ranking.sort_values(
            by="Average_Speed",
            ascending=False
        )

        ranking.reset_index(
            drop=True,
            inplace=True
        )

        ranking.index += 1
        ranking.index.name = "Rank"

        return ranking

    # ==========================================================
    # Traffic Status
    # ==========================================================

    def traffic_status(self):

        if self.df.empty:
            return pd.DataFrame()

        status = (

            self.df

            .groupby(
                "corridor_id",
                as_index=False
            )

            .agg(

                Average_Speed=(
                    "average_speed_kmph",
                    "mean"
                ),

                Average_Travel_Time=(
                    "duration_seconds",
                    "mean"
                ),

                Trips=(
                    "corridor_id",
                    "count"
                )

            )

        )

        status["Average_Speed"] = (
            status["Average_Speed"]
            .round(2)
        )

        status["Average_Travel_Time"] = (
            status["Average_Travel_Time"] / 60
        ).round(2)

        def classify(speed):

            if speed >= 40:
                return "🟢 Normal"

            elif speed >= 25:
                return "🟡 Moderate"

            return "🔴 Heavy"

        status["Traffic_Status"] = (
            status["Average_Speed"]
            .apply(classify)
        )

        return status.sort_values(
            by="Average_Speed",
            ascending=False
        )

    # ==========================================================
    # Hourly Summary
    # ==========================================================

    def hourly_summary(self):

        if self.df.empty:
            return pd.DataFrame()

        summary = (

            self.df

            .groupby(
                "hour",
                as_index=False
            )

            .agg(

                Average_Speed=(
                    "average_speed_kmph",
                    "mean"
                ),

                Average_Travel_Time=(
                    "duration_seconds",
                    "mean"
                ),

                Trips=(
                    "hour",
                    "count"
                )

            )

        )

        summary["Average_Speed"] = (
            summary["Average_Speed"]
            .round(2)
        )

        summary["Average_Travel_Time"] = (
            summary["Average_Travel_Time"] / 60
        ).round(2)

        return summary

    # ==========================================================
    # Direction Summary
    # ==========================================================

    def direction_summary(self):

        if self.df.empty:
            return pd.DataFrame()

        summary = (

            self.df

            .groupby(
                "direction",
                as_index=False
            )

            .agg(

                Average_Speed=(
                    "average_speed_kmph",
                    "mean"
                ),

                Average_Travel_Time=(
                    "duration_seconds",
                    "mean"
                ),

                Trips=(
                    "direction",
                    "count"
                )

            )

        )

        summary["Average_Speed"] = (
            summary["Average_Speed"]
            .round(2)
        )

        summary["Average_Travel_Time"] = (
            summary["Average_Travel_Time"] / 60
        ).round(2)

        return summary

    # ==========================================================
    # Corridor Statistics
    # ==========================================================

    def corridor_statistics(self):

        if self.df.empty:
            return pd.DataFrame()

        stats = (

            self.df

            .groupby(
                "corridor_id",
                as_index=False
            )

            .agg(

                Average_Speed=(
                    "average_speed_kmph",
                    "mean"
                ),

                Minimum_Speed=(
                    "average_speed_kmph",
                    "min"
                ),

                Maximum_Speed=(
                    "average_speed_kmph",
                    "max"
                ),

                Average_Travel_Time=(
                    "duration_seconds",
                    "mean"
                ),

                Total_Trips=(
                    "corridor_id",
                    "count"
                )

            )

        )

        stats["Average_Speed"] = (
            stats["Average_Speed"]
            .round(2)
        )

        stats["Minimum_Speed"] = (
            stats["Minimum_Speed"]
            .round(2)
        )

        stats["Maximum_Speed"] = (
            stats["Maximum_Speed"]
            .round(2)
        )

        stats["Average_Travel_Time"] = (
            stats["Average_Travel_Time"] / 60
        ).round(2)

        return stats