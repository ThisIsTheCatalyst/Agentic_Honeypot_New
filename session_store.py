import json
import logging
import time
from redis.exceptions import RedisError
from redis_client import redis_client

SESSION_TTL_SECONDS = 3600  

logger = logging.getLogger(__name__)



def get_session(session_id: str) -> dict:
    key = f"session:{session_id}"

    try:
        raw = redis_client.get(key)
    except RedisError as e:
        logger.error("Redis GET failed: %s", e)
        raw = None 

    if raw:
        session = json.loads(raw)
        if "started_at" not in session:
            session["started_at"] = time.time()
        return session

    
    session = {
        "messages": [],
        "agent_state": {
            "turns": 0,
            "stall_count": 0,
            "current_strategy": "delay",
            "last_language": "english",
            "used_templates": [],
            "llm_calls": 0
        },
        "intelligence": {
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": [],
            "bankAccounts": [],
            "emailAddresses": [],
            "caseIds": [],
            "policyNumbers": [],
            "orderNumbers": []
        },
        "scam_detected": True,
        "finalized": False,
        "started_at": time.time()
    }

    try:
        redis_client.setex(
            key,
            SESSION_TTL_SECONDS,
            json.dumps(session)
        )
    except RedisError as e:
        logger.error("Redis SET failed: %s", e)

    return session



def save_session(session_id: str, session: dict) -> None:
    key = f"session:{session_id}"

    try:
        redis_client.setex(
            key,
            SESSION_TTL_SECONDS,
            json.dumps(session)
        )
    except RedisError as e:
        logger.error("Redis SET failed: %s", e)
