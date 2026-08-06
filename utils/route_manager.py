import pandas as pd
from pathlib import Path


class RouteManager:
    """
    Responsible for loading and managing traffic routes.
    """

    def __init__(self):

        project_root = Path(__file__).resolve().parent.parent

        self.route_file = project_root / "routes" / "guntur_routes.csv"

    def load_routes(self):

        routes = pd.read_csv(self.route_file)

        return routes