import redis
from typing import Optional
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Cliente Redis singleton para caching"""
    _instance: Optional[redis.Redis] = None
    _enabled: bool = settings.REDIS_ENABLED
    
    @classmethod
    def get_client(cls) -> Optional[redis.Redis]:
        """Obtener instancia de Redis (singleton)"""
        if not cls._enabled:
            return None
            
        if cls._instance is None:
            try:
                cls._instance = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                cls._instance.ping()
                logger.info(f"✅ Redis conectado: {settings.REDIS_URL}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo conectar a Redis: {e}. Caché deshabilitado.")
                cls._instance = None
                cls._enabled = False
        
        return cls._instance
    
    @classmethod
    def is_available(cls) -> bool:
        """Verificar si Redis está disponible"""
        if not cls._enabled:
            return False
        try:
            client = cls.get_client()
            if client:
                client.ping()
                return True
        except Exception:
            pass
        return False
    
    @classmethod
    def close(cls):
        """Cerrar conexión a Redis"""
        if cls._instance:
            try:
                cls._instance.close()
                logger.info("Redis conexión cerrada")
            except Exception as e:
                logger.error(f"Error cerrando Redis: {e}")
            finally:
                cls._instance = None


def get_redis() -> Optional[redis.Redis]:
    """Dependency para obtener cliente Redis"""
    return RedisClient.get_client()


def cache_key(prefix: str, **kwargs) -> str:
    """Generar clave de caché consistente"""
    parts = [prefix]
    for key, value in sorted(kwargs.items()):
        if value is not None:
            parts.append(f"{key}:{value}")
    return ":".join(parts)


def serialize_for_cache(data) -> str:
    """Serializar datos para caché"""
    if hasattr(data, 'model_dump'):
        # Pydantic model
        return json.dumps(data.model_dump(), default=str)
    elif hasattr(data, '__dict__'):
        # SQLAlchemy model
        return json.dumps({
            c.name: getattr(data, c.name)
            for c in data.__table__.columns
        }, default=str)
    else:
        return json.dumps(data, default=str)


def deserialize_from_cache(data_str: str) -> dict:
    """Deserializar datos del caché"""
    return json.loads(data_str)

