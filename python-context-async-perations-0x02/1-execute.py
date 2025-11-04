# 1-execute.py
import sqlite3
from db_utils import log_query

class ExecuteQuery:
    """Reusable context manager to execute queries"""

    def __init__(self, query, params=()):
        self.query = query
        self.params = params

    def __enter__(self):
        log_query("Opening database for query execution")
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()
        log_query("Query execution complete and connection closed")

# Usage
if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    with ExecuteQuery(query, params) as results:
        for row in results:
            print(row)
