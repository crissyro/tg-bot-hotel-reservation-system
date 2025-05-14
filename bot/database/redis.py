import redis.asyncio as redis
from config import config
import logging


class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        try:
            self.client = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db,
                password=config.redis_password.get_secret_value() if config.redis_password else None,
                decode_responses=True
            )
            await self.client.ping()
            logging.info("Successfully connected to Redis!")
            
        except Exception as e:
            logging.error(f"Redis connection error: {e}")
            raise

    async def close(self):
        if self.client:
            await self.client.close()
            logging.info("Redis connection closed.")


redis_client = RedisClient()

async def set_key(key: str, value: str, ex: int = 3600):
    await redis_client.connect()
    await redis_client.client.set(name=key, value=value, ex=ex)

async def get_key(key: str) -> str:
    await redis_client.connect()
    return await redis_client.client.get(name=key)

async def delete_key(key: str):
    await redis_client.connect()
    await redis_client.client.delete(key)