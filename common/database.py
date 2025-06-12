import sqlite3
import os
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "../data/twitter.db")

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                followers_count INTEGER DEFAULT 0,
                following_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                retweets INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            CREATE INDEX IF NOT EXISTS idx_tweets_user_id ON tweets(user_id);
            CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets(created_at);
        """)

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close() 