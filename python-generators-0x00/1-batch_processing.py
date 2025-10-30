from typing import Generator, List, Dict, Any
import seed

def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    conn = seed.connect_to_prodev()
    if not conn:
        return
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT user_id, name, email, age FROM user_data;")
        batch = cur.fetchmany(size=batch_size)
        while batch:
            yield [
                {"user_id": r["user_id"], "name": r["name"], "email": r["email"], "age": int(r["age"])}
                for r in batch
            ]
            batch = cur.fetchmany(size=batch_size)
        cur.close()
    finally:
        conn.close()

def batch_processing(batch_size: int = 50) -> None:
    for batch in stream_users_in_batches(batch_size):  # loop 1
        for user in batch:                             # loop 2
            if user["age"] > 25:
                print(user)

