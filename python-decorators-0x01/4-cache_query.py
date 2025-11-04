#!/usr/bin/env python3
import sqlite3
import functools

query_cache = {}

def with_db_connection(func):
    """Open/close connection automatically"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper

def cache_query(func):
    """Cache query results to avoid redundant calls"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query = kwargs.get("query") or (args[0] if args else "")
        if query in query_cache:
            print("[CACHE] Returning cached result.")
            return query_cache[query]
        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        print("[CACHE] Query result cached.")
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call (not cached)
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call (cached)
users_again = fetch_users_with_cache(query="SELECT * FROM users")
