from redis.asyncio import Redis
from dotenv import load_dotenv
import os


load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("Missing required value: REDIS_URL")

redis = Redis.from_url(REDIS_URL)

async def set_token(key: str, value: str, ttl: int) -> None:
   await redis.set(key, value, ex=ttl)

async def get_token(key: str) -> str | None:
    return await redis.get(key)