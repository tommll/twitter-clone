from fastapi import FastAPI, HTTPException
from common.models import Tweet, User
from common.cache import redis_client
import json

app = FastAPI(title="Twitter Clone - Write Service")

@app.post("/tweets", response_model=Tweet)
async def create_tweet(tweet: Tweet):
    # Publish tweet to Redis for processing
    message = {
        "type": "create_tweet",
        "data": tweet.dict()
    }
    redis_client.rpush("tweet_queue", json.dumps(message))
    return tweet

@app.post("/users", response_model=User)
async def create_user(user: User):
    # Publish user creation to Redis for processing
    message = {
        "type": "create_user",
        "data": user.dict()
    }
    redis_client.rpush("user_queue", json.dumps(message))
    return user

@app.post("/tweets/{tweet_id}/like")
async def like_tweet(tweet_id: int):
    message = {
        "type": "like_tweet",
        "data": {"tweet_id": tweet_id}
    }
    redis_client.rpush("tweet_queue", json.dumps(message))
    return {"status": "success"}

@app.post("/tweets/{tweet_id}/retweet")
async def retweet(tweet_id: int):
    message = {
        "type": "retweet",
        "data": {"tweet_id": tweet_id}
    }
    redis_client.rpush("tweet_queue", json.dumps(message))
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 