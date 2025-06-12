from fastapi import FastAPI, HTTPException
from common.models import Tweet, User
from common.cache import redis_client
import json

app = FastAPI(title="Twitter Clone - Write Service")

# Define stream names
TWEET_STREAM = "tweet_stream"
USER_STREAM = "user_stream"

@app.post("/tweets", response_model=Tweet)
async def create_tweet(tweet: Tweet):
    # Publish tweet to Redis Stream
    message = {
        "type": "create_tweet",
        "data": tweet.dict()
    }
    # Use XADD to add message to tweet stream
    redis_client.xadd(TWEET_STREAM, {"message": json.dumps(message)})
    return tweet

@app.post("/users", response_model=User)
async def create_user(user: User):
    # Publish user creation to Redis Stream
    message = {
        "type": "create_user",
        "data": user.dict()
    }
    # Use XADD to add message to user stream
    redis_client.xadd(USER_STREAM, {"message": json.dumps(message)})
    return user

@app.post("/tweets/{tweet_id}/like")
async def like_tweet(tweet_id: int):
    message = {
        "type": "like_tweet",
        "data": {"tweet_id": tweet_id}
    }
    # Use XADD to add like event to tweet stream
    redis_client.xadd(TWEET_STREAM, {"message": json.dumps(message)})
    return {"status": "success"}

@app.post("/tweets/{tweet_id}/retweet")
async def retweet(tweet_id: int):
    message = {
        "type": "retweet",
        "data": {"tweet_id": tweet_id}
    }
    # Use XADD to add retweet event to tweet stream
    redis_client.xadd(TWEET_STREAM, {"message": json.dumps(message)})
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)