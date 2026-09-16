import json
import logging
from typing import Optional, Any

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from app.config.settings import settings

logger = logging.getLogger("manabi.cache.redis")


class RedisClient:
    """
    Redis manager for ephemeral caching, rate-limiting, and distributed locking.
    Degrades gracefully if Redis is unavailable.
    """

    def __init__(self):
        self._redis = None

    @property
    def is_available(self) -> bool:
        return aioredis is not None and self._redis is not None

    async def get_client(self):
        if aioredis is None:
            return None
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2.0,
                )
                await self._redis.ping()
            except Exception as exc:
                logger.warning(f"Redis unavailable ({exc}). Ephemeral caching degraded.")
                self._redis = None
        return self._redis

    async def get(self, key: str) -> Optional[str]:
        client = await self.get_client()
        if not client:
            return None
        try:
            return await client.get(key)
        except Exception:
            return None

    async def set(self, key: str, value: str, ttl_seconds: int = 300) -> bool:
        client = await self.get_client()
        if not client:
            return False
        try:
            await client.set(key, value, ex=ttl_seconds)
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        client = await self.get_client()
        if not client:
            return False
        try:
            await client.delete(key)
            return True
        except Exception:
            return False


redis_client = RedisClient()
