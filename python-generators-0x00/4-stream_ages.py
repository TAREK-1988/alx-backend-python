import seed

def stream_user_ages():
    conn = seed.connect_to_prodev()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT age FROM user_data;")
        row = cur.fetchone()
        while row:          # loop 1
            yield int(row[0])
            row = cur.fetchone()
        cur.close()
    finally:
        conn.close()

def compute_average_age():
    total = 0
    count = 0
    for age in stream_user_ages():  # loop 2
        total += age
        count += 1
    avg = (total / count) if count else 0
    print(f"Average age of users: {avg:.2f}")

if __name__ == "__main__":
    compute_average_age()

