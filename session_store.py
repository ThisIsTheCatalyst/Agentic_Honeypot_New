import json
from .redis_client import redis_client

SESSION_TTL_SECONDS = 3600  # ~1 hour

def get_session(session_id: str):
    key = f"session:{session_id}"
    data = redis_client.get(key)

    if data is None:
        return None

    return json.loads(data)


def save_session(session_id: str, session: dict):
    key = f"session:{session_id}"

    redis_client.setex(
        key,
        SESSION_TTL_SECONDS,
        json.dumps(session)
    )