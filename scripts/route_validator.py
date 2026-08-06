import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import folium
import polyline

from services.google_routes import GoogleRoutesService
from utils.route_manager import RouteManager


def main():

    # Create maps folder if it doesn't exist
    project_root = Path(__file__).resolve().parent.parent
    maps_folder = project_root / "maps"
    maps_folder.mkdir(exist_ok=True)

    # Load routes
    route_manager = RouteManager()
    routes = route_manager.load_routes()

    # Google Routes API
    google_service = GoogleRoutesService()

    print("=" * 70)
    print("GENERATING ROUTE MAPS")
    print("=" * 70)

    for _, route in routes.iterrows():

        print(
            f"Processing Corridor {route['Corridor_ID']} "
            f"({route['Direction']})..."
        )

        result = google_service.get_route_data(route)

        if result is None:
            print("Google API Error")
            continue

        if "routes" not in result:
            print("No route returned by Google.")
            continue

        api_route = result["routes"][0]

        # Distance (km)
        distance = api_route["distanceMeters"] / 1000

        # Duration
        duration = api_route["duration"]

        # Encoded polyline
        encoded_polyline = api_route["polyline"]["encodedPolyline"]

        # Decode to latitude/longitude pairs
        coordinates = polyline.decode(encoded_polyline)

        # Origin & destination
        origin = [
            float(route["Origin_Lat"]),
            float(route["Origin_Lng"])
        ]

        destination = [
            float(route["Destination_Lat"]),
            float(route["Destination_Lng"])
        ]

        # Create map
        m = folium.Map(
            location=origin,
            zoom_start=16
        )

        # Origin marker
        folium.Marker(
            location=origin,
            popup=f"Origin<br>{route['Origin_Name']}",
            tooltip="Origin",
            icon=folium.Icon(color="green")
        ).add_to(m)

        # Destination marker
        folium.Marker(
            location=destination,
            popup=f"Destination<br>{route['Destination_Name']}",
            tooltip="Destination",
            icon=folium.Icon(color="red")
        ).add_to(m)

        # Draw route
        folium.PolyLine(
            coordinates,
            weight=6,
            color="blue",
            opacity=0.8,
            tooltip=(
                f"Distance: {distance:.2f} km<br>"
                f"Duration: {duration}"
            )
        ).add_to(m)

        # Save HTML
        filename = (
            f"Corridor_"
            f"{int(route['Corridor_ID']):02d}_"
            f"{route['Direction']}.html"
        )

        m.save(maps_folder / filename)

    print("\n" + "=" * 70)
    print("ALL ROUTE MAPS GENERATED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nMaps saved in:\n{maps_folder}")


if __name__ == "__main__":
    main()