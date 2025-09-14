import redis.asyncio as redis
import json
import hashlib
from typing import Any, Optional, Dict
from config import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
        return f"{prefix}:{key_hash}"
    
    async def get_inventory_cache(self, sku: str, warehouse_code: str = None) -> Optional[Dict]:
        """Get inventory data from cache"""
        cache_key = self._generate_key("inventory", sku=sku, warehouse=warehouse_code)
        
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get failed for {cache_key}: {e}")
        
        return None
    
    async def set_inventory_cache(self, sku: str, data: Dict, warehouse_code: str = None):
        """Cache inventory data"""
        cache_key = self._generate_key("inventory", sku=sku, warehouse=warehouse_code)
        
        try:
            await self.redis.setex(
                cache_key,
                settings.CACHE_TTL_INVENTORY,
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache set failed for {cache_key}: {e}")
    
    async def get_order_status_cache(self, order_number: str) -> Optional[Dict]:
        """Get order status from cache"""
        cache_key = self._generate_key("order_status", order_number=order_number)
        
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get failed for {cache_key}: {e}")
        
        return None
    
    async def set_order_status_cache(self, order_number: str, data: Dict):
        """Cache order status data"""
        cache_key = self._generate_key("order_status", order_number=order_number)
        
        try:
            await self.redis.setex(
                cache_key,
                settings.CACHE_TTL_ORDER_STATUS,
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache set failed for {cache_key}: {e}")
    
    async def get_product_location_cache(self, sku: str) -> Optional[Dict]:
        """Get product location from cache"""
        cache_key = self._generate_key("product_location", sku=sku)
        
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get failed for {cache_key}: {e}")
        
        return None
    
    async def set_product_location_cache(self, sku: str, data: Dict):
        """Cache product location data"""
        cache_key = self._generate_key("product_location", sku=sku)
        
        try:
            await self.redis.setex(
                cache_key,
                settings.CACHE_TTL_PRODUCT_INFO,
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache set failed for {cache_key}: {e}")
    
    async def invalidate_inventory_cache(self, sku: str):
        """Invalidate inventory cache for a product"""
        pattern = f"inventory:*{sku}*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
    
    async def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            info = await self.redis.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "used_memory_human": info.get("used_memory_human", "0B")
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}

# Global cache service instance
cache_service = CacheService()
