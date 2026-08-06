import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import sqlite3
import pandas as pd


def get_traffic_status(speed):

    if speed < 15:
        return "🔴 Heavy Congestion"

    elif speed < 25:
        return "🟡 Moderate Traffic"

    else:
        return "🟢 Free Flow"


def main():

    # Locate project folder
    project_root = Path(__file__).resolve().parent.parent

    db_path = project_root / "database" / "traffic.db"

    # Connect to database
    connection = sqlite3.connect(db_path)

    # Read database
    df = pd.read_sql_query(
        "SELECT * FROM traffic_data",
        connection
    )

    if df.empty:
        print("\nNo traffic data found in database. Run collector.py first.")
        connection.close()
        return

    # Corridor-wise summary
    corridor_summary = (
        df.groupby("corridor_id")
        .agg(
            Average_Speed=("average_speed_kmph", "mean"),
            Average_Travel_Time=("duration_seconds", "mean"),
            Average_Distance=("distance_km", "mean"),
            Total_Observations=("corridor_id", "count")
        )
        .reset_index()
    )

    # Round values
    corridor_summary["Average_Speed"] = (
        corridor_summary["Average_Speed"].round(2)
    )

    corridor_summary["Average_Travel_Time"] = (
        corridor_summary["Average_Travel_Time"].round(0)
    )

    corridor_summary["Average_Distance"] = (
        corridor_summary["Average_Distance"].round(2)
    )

    # Add traffic status
    corridor_summary["Traffic_Status"] = (
        corridor_summary["Average_Speed"]
        .apply(get_traffic_status)
    )

    # Sort by average speed
    corridor_summary = corridor_summary.sort_values(
        by="Average_Speed"
    )

    print("\n" + "=" * 100)
    print("                     GUNTUR TRAFFIC ANALYTICS REPORT")
    print("=" * 100)

    print(corridor_summary.to_string(index=False))

    connection.close()


if __name__ == "__main__":
    main()