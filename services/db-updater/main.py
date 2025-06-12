import json
import time
import asyncio
from common.cache import redis_client
from common.database import get_db, init_db

# Define stream names
TWEET_STREAM = "tweet_stream"
USER_STREAM = "user_stream"

def process_tweet_message(message):
    data = json.loads(message)["data"]
    msg_type = json.loads(message)["type"]

    with get_db() as conn:
        if msg_type == "create_tweet":
            conn.execute("""
                INSERT INTO tweets (content, user_id, created_at)
                VALUES (?, ?, datetime('now'))
            """, (data["content"], data["user_id"]))
            conn.commit()

        elif msg_type == "like_tweet":
            conn.execute("""
                UPDATE tweets
                SET likes = likes + 1
                WHERE id = ?
            """, (data["tweet_id"],))
            conn.commit()

        elif msg_type == "retweet":
            conn.execute("""
                UPDATE tweets
                SET retweets = retweets + 1
                WHERE id = ?
            """, (data["tweet_id"],))
            conn.commit()

def process_user_message(message):
    data = json.loads(message)["data"]
    
    with get_db() as conn:
        conn.execute("""
            INSERT INTO users (username, email, created_at)
            VALUES (?, ?, datetime('now'))
        """, (data["username"], data["email"]))
        conn.commit()

async def main():
    print("Starting DB updater service...")
    init_db()  # Initialize database tables

    # Initialize stream IDs
    tweet_stream_id = "0"  # Start from beginning
    user_stream_id = "0"   # Start from beginning

    # Create consumer group for each stream
    try:
        await redis_client.xgroup_create(TWEET_STREAM, "db-updater-group", "0", mkstream=True)
    except:
        print("Tweet stream group already exists")

    try:
        await redis_client.xgroup_create(USER_STREAM, "db-updater-group", "0", mkstream=True)
    except:
        print("User stream group already exists")

    while True:
        try:
            # Read from both streams
            streams = await redis_client.xreadgroup(
                "db-updater-group",
                "db-updater-consumer",
                {
                    TWEET_STREAM: ">",  # Read new messages
                    USER_STREAM: ">"    # Read new messages
                },
                count=10,  # Process 10 messages at a time
                block=1000  # Block for 1 second if no messages
            )

            for stream_name, messages in streams:
                for message_id, message_data in messages:
                    if stream_name == TWEET_STREAM.encode():
                        process_tweet_message(message_data[b"message"].decode())
                        redis_client.xack(TWEET_STREAM, "db-updater-group", message_id)
                    elif stream_name == USER_STREAM.encode():
                        process_user_message(message_data[b"message"].decode())
                        redis_client.xack(USER_STREAM, "db-updater-group", message_id)

        except Exception as e:
            print(f"Error processing messages: {e}")
            time.sleep(1)  # Wait before retrying

if __name__ == "__main__":
    asyncio.run(main()) 