import sqlite3
import pandas as pd

from pathlib import Path

try:
    from dashboard.config import DATABASE_PATH
except ImportError:
    from config import DATABASE_PATH


class DataLoader:

    def __init__(self):

        self.database = Path(DATABASE_PATH).resolve()

    def load_data(self):

        if not self.database.exists():
            return pd.DataFrame()

        db_str = str(self.database)
        try:
            connection = sqlite3.connect(f"file:{self.database.as_posix()}?mode=ro", uri=True, timeout=30.0)
        except Exception:
            connection = sqlite3.connect(db_str, timeout=30.0)

        cursor = connection.cursor()

        query = """
        SELECT 
            id,
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
        FROM traffic_data
        ORDER BY collection_date DESC,
                 collection_time DESC
        """

        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
        except Exception:
            df = pd.DataFrame()
        finally:
            connection.close()

        return df

