import os
import redis

# ----------------------------
# Redis configuration
# ----------------------------
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]

# ----------------------------
# Redis client (singleton)
# ----------------------------
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True  # IMPORTANT: returns strings, not bytes
)
