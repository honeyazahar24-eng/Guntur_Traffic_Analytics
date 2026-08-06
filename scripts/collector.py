import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from datetime import datetime

from utils.route_manager import RouteManager
from services.google_routes import GoogleRoutesService
from database.database import TrafficDatabase


def main():

    # Create objects
    route_manager = RouteManager()
    google_service = GoogleRoutesService()
    database = TrafficDatabase()

    # Load all routes
    routes = route_manager.load_routes()

    print("\n" + "=" * 80)
    print("               GUNTUR TRAFFIC DATA COLLECTOR")
    print("=" * 80)

    # Process every route
    for index, route in routes.iterrows():

        result = google_service.get_route_data(route)

        if not result or "routes" not in result:
            print(f"\n❌ Google API failed for Route {index + 1}")
            continue

        # Extract Google API response
        distance_km = result["routes"][0]["distanceMeters"] / 1000

        duration_seconds = int(
            result["routes"][0]["duration"].replace("s", "")
        )

        # Calculate average speed
        hours = duration_seconds / 3600

        if hours > 0:
            average_speed = distance_km / hours
        else:
            average_speed = 0

        # Current date and time
        current_time = datetime.now()

        # Store in database
        database.insert_record(
            collection_date=current_time.strftime("%Y-%m-%d"),
            collection_time=current_time.strftime("%H:%M:%S"),
            day_name=current_time.strftime("%A"),
            hour=current_time.hour,
            corridor_id=int(route["Corridor_ID"]),
            direction=route["Direction"],
            origin_name=route["Origin_Name"].strip(),
            destination_name=route["Destination_Name"].strip(),
            distance_km=distance_km,
            duration_seconds=duration_seconds,
            average_speed_kmph=average_speed
        )

        # Convert duration into minutes and seconds
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60

        # Display report
        print("\n" + "-" * 80)
        print(f"Route Number     : {index + 1}")
        print(f"Corridor ID      : {route['Corridor_ID']}")
        print(f"Direction        : {route['Direction']}")
        print()
        print(f"Origin           : {route['Origin_Name'].strip()}")
        print(f"Destination      : {route['Destination_Name'].strip()}")
        print()
        print(f"Distance         : {distance_km:.2f} km")
        print(f"Travel Time      : {minutes} min {seconds} sec")
        print(f"Average Speed    : {average_speed:.2f} km/h")
        print(f"Collection Date  : {current_time.strftime('%Y-%m-%d')}")
        print(f"Collection Time  : {current_time.strftime('%H:%M:%S')}")
        print(f"Day              : {current_time.strftime('%A')}")
        print("Status           : SUCCESS")

    database.close()

    print("\n" + "=" * 80)
    print("Traffic Collection Completed Successfully")
    print("=" * 80)


if __name__ == "__main__":
    main()