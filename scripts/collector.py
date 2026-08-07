import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from datetime import datetime, timezone, timedelta


from utils.route_manager import RouteManager
from services.google_routes import GoogleRoutesService
from database.database import TrafficDatabase


# Force UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


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
            print(f"\n[X] Google API failed for Route {index + 1}")
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

        # Current date and time in IST (Indian Standard Time, UTC+5:30)
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        current_time = datetime.now(ist_tz)


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

    # Update scheduler_status.json with IST timestamp
    try:
        import json
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(ist_tz)

        
        status_file = project_root / "logs" / "scheduler_status.json"
        status_file.parent.mkdir(exist_ok=True)
        
        check_db = TrafficDatabase()
        check_db.cursor.execute("SELECT COUNT(*) FROM traffic_data")
        total_records = check_db.cursor.fetchone()[0]
        check_db.close()

        status_data = {
            "status": "success",
            "message": f"Last successful run at {now_ist.strftime('%Y-%m-%d %H:%M:%S IST')} — {total_records} total records",
            "last_run": now_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
            "last_record_count": total_records,
            "next_run": "Every 30 min (:00 & :30 IST)"
        }
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2)
    except Exception:
        pass

    print("\n" + "=" * 80)
    print("Traffic Collection Completed Successfully")
    print("=" * 80)

    # Attempt automatic push to GitHub if GH_PAT is present
    push_db_to_github()


def push_db_to_github():
    """Push updated traffic.db to GitHub repository via REST API if token is configured."""
    try:
        import base64
        import urllib.request
        import json
        import os

        token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
        if not token:
            try:
                import streamlit as st
                token = st.secrets.get("GH_PAT")
            except Exception:
                token = None

        if not token:
            return

        owner = "honeyazahar24-eng"
        repo = "Guntur_Traffic_Analytics"
        db_path = project_root / "database" / "traffic.db"
        if not db_path.exists():
            return

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/database/traffic.db"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Guntur-Traffic-Collector"
        }

        sha = None
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                sha = data.get("sha")
        except Exception:
            pass

        content_b64 = base64.b64encode(db_path.read_bytes()).decode('utf-8')
        payload = {
            "message": "Auto-updated traffic.db from Cloud Collector [skip ci]",
            "content": content_b64,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method="PUT"
        )
        with urllib.request.urlopen(req) as resp:
            print("Successfully auto-committed updated traffic.db to GitHub via API!")
    except Exception as e:
        print(f"GitHub API push notice: {e}")


if __name__ == "__main__":
    main()