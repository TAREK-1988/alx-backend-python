from typing import List, Dict, Any
import seed

def paginate_users(page_size: int, offset: int) -> List[Dict[str, Any]]:
    conn = seed.connect_to_prodev()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s", (page_size, offset))
        rows = cur.fetchall()
        cur.close()
        for r in rows:
            r["age"] = int(r["age"])
        return rows
    finally:
        conn.close()

def lazy_pagination(page_size: int):
    offset = 0
    while True:  # loop الوحيدة
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size

