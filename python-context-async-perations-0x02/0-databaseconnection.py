# 0-databaseconnection.py
import sqlite3
from db_utils import log_query

class DatabaseConnection:
    """Custom context manager for database connection"""

    def __enter__(self):
        log_query("Connecting to database")
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()
        log_query("Database connection closed")

# Usage
if __name__ == "__main__":
    with DatabaseConnection() as cursor:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
