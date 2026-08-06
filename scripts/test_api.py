import sys
from pathlib import Path
import os

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.google_routes import GoogleRoutesService
from utils.route_manager import RouteManager


def main():
    print("=" * 70)
    print("TESTING GOOGLE ROUTES SERVICE API")
    print("=" * 70)

    route_manager = RouteManager()
    routes = route_manager.load_routes()

    if routes.empty:
        print("FAIL: No routes found in guntur_routes.csv")
        return

    google_service = GoogleRoutesService()
    sample_route = routes.iloc[0]

    print(f"Testing Route 1: {sample_route['Origin_Name'].strip()} -> {sample_route['Destination_Name'].strip()}")
    result = google_service.get_route_data(sample_route)

    if result and "routes" in result and len(result["routes"]) > 0:
        api_route = result["routes"][0]
        distance_km = api_route["distanceMeters"] / 1000
        duration_sec = int(api_route["duration"].replace("s", ""))
        print("PASS: API Response Received:")
        print(f"   - Distance: {distance_km:.2f} km")
        print(f"   - Duration: {duration_sec // 60} min {duration_sec % 60} sec")
    else:
        print("FAIL: API Test Failed: Invalid or empty response")


if __name__ == "__main__":
    main()
