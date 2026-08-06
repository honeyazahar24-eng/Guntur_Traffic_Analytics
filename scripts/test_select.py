import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.database import TrafficDatabase


def main():

    database = TrafficDatabase()

    database.cursor.execute("""
        SELECT *
        FROM traffic_data
        ORDER BY id
    """)

    records = database.cursor.fetchall()

    print("\n" + "=" * 120)
    print("                         GUNTUR TRAFFIC DATABASE")
    print("=" * 120)

    for record in records:

        print(f"""
ID                 : {record[0]}
Collection Date    : {record[1]}
Collection Time    : {record[2]}
Day                : {record[3]}
Hour               : {record[4]}
Corridor ID        : {record[5]}
Direction          : {record[6]}
Origin             : {record[7]}
Destination        : {record[8]}
Distance           : {record[9]:.2f} km
Travel Time        : {record[10]} sec
Average Speed      : {record[11]:.2f} km/h
{"-" * 120}
""")

    database.close()


if __name__ == "__main__":
    main()