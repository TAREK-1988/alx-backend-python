
from typing import Generator, Dict, Any
import seed

def stream_users() -> Generator[Dict[str, Any], None, None]:
    """Yield one row at a time (single loop)."""
    conn = seed.connect_to_prodev()
    if not conn:
        return
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT user_id, name, email, age FROM user_data;")
        row = cur.fetchone()
        while row:
            yield {
                "user_id": row["user_id"],
                "name": row["name"],
                "email": row["email"],
                "age": int(row["age"]),
            }
            row = cur.fetchone()
        cur.close()
    finally:
        conn.close()
