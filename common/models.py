from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Tweet(BaseModel):
    id: Optional[int] = None
    content: str
    user_id: int
    created_at: datetime = datetime.utcnow()
    likes: int = 0
    retweets: int = 0

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    created_at: datetime = datetime.utcnow()
    followers_count: int = 0
    following_count: int = 0

class TweetResponse(Tweet):
    user: User 