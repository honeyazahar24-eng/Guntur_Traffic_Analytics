class KPI:

    @staticmethod
    def calculate(df):

        if df.empty:

            return {
                "total_records": 0,
                "average_speed": 0,
                "average_travel_time": 0,
                "latest_date": "N/A",
                "active_routes": 0
            }

        return {

            "total_records": len(df),

            "average_speed": round(
                df["average_speed_kmph"].mean(),
                2
            ),

            "average_travel_time": round(
                df["duration_seconds"].mean() / 60,
                2
            ),

            "latest_date": str(
                df["collection_date"].max()
            ),

            "active_routes": df["corridor_id"].nunique()
        }