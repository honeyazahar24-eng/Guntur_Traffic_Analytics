import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.database import TrafficDatabase


def main():

    db = TrafficDatabase()

    db.create_table()

    db.close()


if __name__ == "__main__":
    main()