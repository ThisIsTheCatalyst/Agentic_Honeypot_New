import os
import redis

redis_client = redis.from_url(os.getenv("REDIS_URL"))
# Create Redis client with password support
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)
