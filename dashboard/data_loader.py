import sqlite3
import pandas as pd

try:
    from dashboard.config import DATABASE_PATH
except ImportError:
    from config import DATABASE_PATH


class DataLoader:

    def __init__(self):

        self.database = DATABASE_PATH

    def load_data(self):

        connection = sqlite3.connect(self.database)

        query = """
        SELECT *
        FROM traffic_data
        ORDER BY collection_date DESC,
                 collection_time DESC
        """

        df = pd.read_sql(query, connection)

        connection.close()

        return df