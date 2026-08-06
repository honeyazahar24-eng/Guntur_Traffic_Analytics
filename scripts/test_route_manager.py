import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.route_manager import RouteManager


def main():

    route_manager = RouteManager()

    routes = route_manager.load_routes()

    print("\n========== GUNTUR TRAFFIC ROUTES ==========\n")

    print(routes)

    print("\n===========================================\n")

    print(f"Total Routes Loaded : {len(routes)}")


if __name__ == "__main__":
    main()