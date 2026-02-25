import json
from typing import Any, Optional
from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.core.config import config

class RedisClient:
    """Async Redis client wrapper for the application."""
    
    def __init__(self, redis_url: str = config.REDIS_URL):
        self.redis_url = redis_url
        self._client: Optional[Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        if self._client is None:
            self._client = await Redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def get(self, key: str) -> Optional[dict]:
        """Get a value from Redis and parse as JSON."""
        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            print(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value in Redis with optional expiration (seconds)."""
        try:
            json_value = json.dumps(value)
            if expire:
                await self._client.setex(key, expire, json_value)
            else:
                await self._client.set(key, json_value)
            return True
        except (RedisError, TypeError) as e:
            print(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            await self._client.delete(key)
            return True
        except RedisError as e:
            print(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            return await self._client.exists(key) > 0
        except RedisError as e:
            print(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def incr(self, key: str) -> Optional[int]:
        """Increment a counter in Redis."""
        try:
            return await self._client.incr(key)
        except RedisError as e:
            print(f"Redis INCR error for key {key}: {e}")
            return None
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key."""
        try:
            await self._client.expire(key, seconds)
            return True
        except RedisError as e:
            print(f"Redis EXPIRE error for key {key}: {e}")
            return False


# Global Redis client instance
redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get the global Redis client instance."""
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client


def init_redis(redis_url: str) -> RedisClient:
    """Initialize the global Redis client."""
    global redis_client
    redis_client = RedisClient(redis_url)
    return redis_client
