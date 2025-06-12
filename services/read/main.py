from fastapi import FastAPI, HTTPException
from common.models import Tweet, User, TweetResponse
from common.database import get_db
from common.cache import get_cache, set_cache
from typing import List

app = FastAPI(title="Twitter Clone - Read Service")

@app.get("/tweets/{tweet_id}", response_model=TweetResponse)
async def get_tweet(tweet_id: int):
    # Try cache first
    cache_key = f"tweet:{tweet_id}"
    cached_tweet = get_cache(cache_key)
    if cached_tweet:
        return cached_tweet

    with get_db() as conn:
        # Get tweet and user in a single query
        tweet = conn.execute("""
            SELECT t.*, u.username, u.email, u.created_at as user_created_at,
                   u.followers_count, u.following_count
            FROM tweets t
            JOIN users u ON t.user_id = u.id
            WHERE t.id = ?
        """, (tweet_id,)).fetchone()

        if not tweet:
            raise HTTPException(status_code=404, detail="Tweet not found")

        # Construct response
        response = {
            "id": tweet["id"],
            "content": tweet["content"],
            "user_id": tweet["user_id"],
            "created_at": tweet["created_at"],
            "likes": tweet["likes"],
            "retweets": tweet["retweets"],
            "user": {
                "id": tweet["user_id"],
                "username": tweet["username"],
                "email": tweet["email"],
                "created_at": tweet["user_created_at"],
                "followers_count": tweet["followers_count"],
                "following_count": tweet["following_count"]
            }
        }

        # Cache the response
        set_cache(cache_key, response)
        return response

@app.get("/users/{user_id}/tweets", response_model=List[TweetResponse])
async def get_user_tweets(user_id: int, limit: int = 10, offset: int = 0):
    cache_key = f"user_tweets:{user_id}:{limit}:{offset}"
    cached_tweets = get_cache(cache_key)
    if cached_tweets:
        return cached_tweets

    with get_db() as conn:
        tweets = conn.execute("""
            SELECT t.*, u.username, u.email, u.created_at as user_created_at,
                   u.followers_count, u.following_count
            FROM tweets t
            JOIN users u ON t.user_id = u.id
            WHERE t.user_id = ?
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset)).fetchall()

        response = []
        for tweet in tweets:
            tweet_data = {
                "id": tweet["id"],
                "content": tweet["content"],
                "user_id": tweet["user_id"],
                "created_at": tweet["created_at"],
                "likes": tweet["likes"],
                "retweets": tweet["retweets"],
                "user": {
                    "id": tweet["user_id"],
                    "username": tweet["username"],
                    "email": tweet["email"],
                    "created_at": tweet["user_created_at"],
                    "followers_count": tweet["followers_count"],
                    "following_count": tweet["following_count"]
                }
            }
            response.append(tweet_data)

        set_cache(cache_key, response)
        return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 