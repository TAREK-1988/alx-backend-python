# 2-concurrent.py
import asyncio
import aiosqlite
from db_utils import log_query

async def async_fetch_users():
    log_query("Fetching all users asynchronously")
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

async def async_fetch_older_users():
    log_query("Fetching users older than 40 asynchronously")
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            return await cursor.fetchall()

async def fetch_concurrently():
    users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    print("\n--- All Users ---")
    for user in users:
        print(user)
    print("\n--- Older Users (40+) ---")
    for user in older_users:
        print(user)

if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
