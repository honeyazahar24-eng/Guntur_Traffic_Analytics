import sqlite3
from pathlib import Path


class TrafficDatabase:

    def __init__(self):

        project_root = Path(__file__).resolve().parent.parent

        db_path = project_root / "database" / "traffic.db"

        self.connection = sqlite3.connect(db_path, timeout=30.0)

        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute("PRAGMA busy_timeout=30000;")
            self.cursor.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass

        self.create_table()



    def create_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS traffic_data (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            collection_date TEXT,

            collection_time TEXT,

            day_name TEXT,

            hour INTEGER,

            corridor_id INTEGER,

            direction TEXT,

            origin_name TEXT,

            destination_name TEXT,

            distance_km REAL,

            duration_seconds INTEGER,

            average_speed_kmph REAL,

            UNIQUE(collection_date, collection_time, corridor_id, direction) ON CONFLICT IGNORE

        )

        """)

        self.cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_traffic_unique 
            ON traffic_data(collection_date, collection_time, corridor_id, direction)
        """)

        self.connection.commit()
        self.deduplicate()

    def deduplicate(self):
        """Clean up any existing duplicate records."""
        try:
            self.cursor.execute("""
                DELETE FROM traffic_data
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM traffic_data
                    GROUP BY collection_date, collection_time, corridor_id, direction
                )
            """)
            self.connection.commit()
        except Exception:
            pass

    def insert_record(
        self,
        collection_date,
        collection_time,
        day_name,
        hour,
        corridor_id,
        direction,
        origin_name,
        destination_name,
        distance_km,
        duration_seconds,
        average_speed_kmph
    ):

        self.cursor.execute("""

        INSERT OR IGNORE INTO traffic_data(

            collection_date,
            collection_time,
            day_name,
            hour,
            corridor_id,
            direction,
            origin_name,
            destination_name,
            distance_km,
            duration_seconds,
            average_speed_kmph

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            collection_date,
            collection_time,
            day_name,
            hour,
            corridor_id,
            direction,
            origin_name,
            destination_name,
            distance_km,
            duration_seconds,
            average_speed_kmph

        ))

        self.connection.commit()

    def close(self):

        self.connection.close()