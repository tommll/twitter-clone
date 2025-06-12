import json
import os
from typing import Optional, Any
import redis.asyncio as redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

retry = Retry(ExponentialBackoff(), 3)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, retry=retry)

def set_cache(key: str, value: Any, expire: int = 3600):
    """Set a key-value pair in Redis with expiration in seconds"""
    redis_client.setex(key, expire, json.dumps(value))

def get_cache(key: str) -> Optional[Any]:
    """Get a value from Redis by key"""
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None

def delete_cache(key: str):
    """Delete a key from Redis"""
    redis_client.delete(key)

def clear_cache():
    """Clear all keys from Redis"""
    redis_client.flushall() 