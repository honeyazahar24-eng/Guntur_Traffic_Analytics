import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from datetime import datetime

from database.database import TrafficDatabase


def main():

    db = TrafficDatabase()

    now = datetime.now()
    distance_km = 1.29
    duration_seconds = 301
    hours = duration_seconds / 3600
    average_speed = distance_km / hours if hours > 0 else 0

    db.insert_record(
        collection_date=now.strftime("%Y-%m-%d"),
        collection_time=now.strftime("%H:%M:%S"),
        day_name=now.strftime("%A"),
        hour=now.hour,
        corridor_id=1,
        direction="Forward",
        origin_name="Rythu Bazar RTC",
        destination_name="Lodge Center",
        distance_km=distance_km,
        duration_seconds=duration_seconds,
        average_speed_kmph=average_speed
    )

    print("Successfully inserted test record.")
    db.close()


if __name__ == "__main__":
    main()