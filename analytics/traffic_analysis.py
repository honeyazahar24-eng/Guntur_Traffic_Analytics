import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.database import TrafficDatabase


def main():

    database = TrafficDatabase()

    cursor = database.cursor

    print("\n" + "=" * 80)
    print("              GUNTUR TRAFFIC ANALYTICS")
    print("=" * 80)

    # Total Records
    cursor.execute("""
        SELECT COUNT(*)
        FROM traffic_data
    """)

    total_records = cursor.fetchone()[0]

    print(f"\nTotal Records Collected : {total_records}")

    if total_records == 0:
        print("\nNo traffic data found in database. Run collector.py first.")
        database.close()
        return

    # Average Speed
    cursor.execute("""
        SELECT AVG(average_speed_kmph)
        FROM traffic_data
    """)

    average_speed = cursor.fetchone()[0]

    print(f"Average Speed           : {average_speed:.2f} km/h")

    # Average Travel Time
    cursor.execute("""
        SELECT AVG(duration_seconds)
        FROM traffic_data
    """)

    average_duration = cursor.fetchone()[0]

    print(f"Average Travel Time     : {average_duration:.0f} seconds")

    # Longest Route
    cursor.execute("""
        SELECT
            origin_name,
            destination_name,
            MAX(distance_km)
        FROM traffic_data
    """)

    longest = cursor.fetchone()

    print("\nLongest Route")

    print(f"Origin       : {longest[0]}")
    print(f"Destination  : {longest[1]}")
    print(f"Distance     : {longest[2]:.2f} km")

    # Shortest Route
    cursor.execute("""
        SELECT
            origin_name,
            destination_name,
            MIN(distance_km)
        FROM traffic_data
    """)

    shortest = cursor.fetchone()

    print("\nShortest Route")

    print(f"Origin       : {shortest[0]}")
    print(f"Destination  : {shortest[1]}")
    print(f"Distance     : {shortest[2]:.2f} km")

    # Peak Rush Hour Analytics
    from dashboard.data_loader import DataLoader
    from dashboard.congestion import CongestionAnalyzer
    loader = DataLoader()
    df = loader.load_data()
    if not df.empty:
        rush_scale = CongestionAnalyzer.rush_hour_congestion_scale_0_10(df)
        extra_info = CongestionAnalyzer.extra_time_per_50km(df)
        net_info = CongestionAnalyzer.congested_road_network_pct(df)

        print("\n" + "=" * 80)
        print("    WEEKDAY PEAK RUSH HOUR CONGESTION METRICS (6-10 AM & 4-8 PM)")
        print("=" * 80)
        print(f"Rush Hour Congestion Index (0-10) : {rush_scale} / 10")
        print(f"Extra Time Spent per 50 km        : +{extra_info['extra_time_min']:.1f} minutes (Total: {extra_info['peak_time_min']:.1f} min)")
        print(f"Congested Road Network (%)        : {net_info['congested_pct']}% ({net_info['congested_length_km']} km of {net_info['total_network_km']} km)")
        print(f"Congested Corridors Count         : {net_info['congested_corridors_count']} corridors operating under <25 km/h")
        print("=" * 80)

    database.close()


if __name__ == "__main__":
    main()