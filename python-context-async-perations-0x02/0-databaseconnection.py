#!/usr/bin/env python3
"""
Task 0: Custom class-based context manager for database connection
"""

import sqlite3
from datetime import datetime

class DatabaseConnection:
    """Custom context manager for database connection"""

    def __init__(self, db_name="users.db"):
        """Initialize with the database name"""
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Open the database connection"""
        print(f"[{datetime.now()}] Connecting to database: {self.db_name}")
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
        print(f"[{datetime.now()}] Database connection closed")

# Usage Example
if __name__ == "__main__":
    with DatabaseConnection() as cursor:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
