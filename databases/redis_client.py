import redis.asyncio as aioredis

from settings import settings


class RedisClient:
    def __init__(self):
        self._redis_client = None

    async def init_redis(self):
        self._redis_client = await aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}"
        )

    def get_redis(self):
        if self._redis_client is None:
            raise Exception("Redis client is not initialized.")
        return self._redis_client

    async def close_redis(self):
        if self._redis_client:
            await self._redis_client.close()


redis_client = RedisClient()
