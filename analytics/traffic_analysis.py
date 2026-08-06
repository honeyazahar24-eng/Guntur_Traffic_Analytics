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

    database.close()


if __name__ == "__main__":
    main()