import sqlite3
import os
from datetime import datetime, timedelta

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
DB_PATH = "data/twitter.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        # Create tables
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

        # Insert test users
        test_users = [
            ("john_doe", "john@example.com"),
            ("jane_smith", "jane@example.com"),
            ("bob_wilson", "bob@example.com"),
        ]
        
        conn.executemany(
            "INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)",
            test_users
        )

        # Insert test tweets
        base_time = datetime.utcnow()
        test_tweets = [
            ("Hello Twitter Clone!", 1, base_time - timedelta(minutes=30), 5, 2),
            ("This is a test tweet", 2, base_time - timedelta(minutes=20), 3, 1),
            ("Another test tweet", 1, base_time - timedelta(minutes=15), 2, 0),
            ("Testing the Twitter clone", 3, base_time - timedelta(minutes=10), 7, 3),
            ("Final test tweet", 2, base_time - timedelta(minutes=5), 1, 0),
        ]
        
        conn.executemany(
            """
            INSERT OR IGNORE INTO tweets 
            (content, user_id, created_at, likes, retweets) 
            VALUES (?, ?, ?, ?, ?)
            """,
            test_tweets
        )

        # Update follower counts
        conn.execute("""
            UPDATE users 
            SET followers_count = 2,
                following_count = 1
            WHERE id = 1
        """)
        conn.execute("""
            UPDATE users 
            SET followers_count = 1,
                following_count = 2
            WHERE id = 2
        """)
        conn.execute("""
            UPDATE users 
            SET followers_count = 1,
                following_count = 1
            WHERE id = 3
        """)

        conn.commit()

if __name__ == "__main__":
    print(f"Initializing database at {DB_PATH}...")
    init_db()
    print("Database initialized with test data!") 