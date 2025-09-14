import redis.asyncio as redis
from config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis: redis.Redis = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    async def increment_rate_limit(self, key: str, window_seconds: int) -> int:
        """Increment rate limit counter and return current count"""
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        results = await pipe.execute()
        return results[0]
    
    async def log_access_event(self, user_id: str, event_type: str, metadata: dict):
        """Log security access event"""
        event_key = f"security_event:{user_id}:{event_type}"
        await self.redis.lpush(event_key, str(metadata))
        await self.redis.expire(event_key, 86400)  # 24 hours

# Global Redis client instance
redis_client = RedisClient()
