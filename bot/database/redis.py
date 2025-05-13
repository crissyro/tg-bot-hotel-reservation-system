import redis.asyncio as redis
from aiogram import Bot

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

async def set_value(key: str, value: str, expire: int = 3600):
    await redis_client.set(key, value, ex=expire)

async def get_value(key: str):
    return await redis_client.get(key)
