import redis.asyncio as aioredis
from redis.asyncio import Redis
from typing import Optional, Any
import json
from app.core.config import settings

_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None and settings.REDIS_URL:
        _redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


# ─── Key Builders ─────────────────────────────────────────────────────────────
# Namespaced so Phase 2 agent memory keys don't collide with auth cache keys.

def session_key(session_id: str) -> str:
    """Phase 2: stores LangGraph conversation state."""
    return f"session:{session_id}:state"


def session_history_key(session_id: str) -> str:
    """Phase 2: stores compressed message history."""
    return f"session:{session_id}:history"


def rate_limit_key(user_id: str, endpoint: str) -> str:
    """Phase 5: rate limiting per user per endpoint."""
    return f"ratelimit:{user_id}:{endpoint}"


def user_cache_key(user_id: str) -> str:
    """Cache user profile to avoid repeated DB hits."""
    return f"user:{user_id}:profile"


# ─── Generic Helpers ──────────────────────────────────────────────────────────

async def cache_set(key: str, value: Any, ttl: int = None) -> None:
    client = await get_redis()
    if client is None:
        return
    ttl = ttl or settings.REDIS_TTL_SECONDS
    await client.set(key, json.dumps(value), ex=ttl)


async def cache_get(key: str) -> Optional[Any]:
    client = await get_redis()
    if client is None:
        return None
    raw = await client.get(key)
    return json.loads(raw) if raw else None


async def cache_delete(key: str) -> None:
    client = await get_redis()
    if client is None:
        return
    await client.delete(key)


async def cache_exists(key: str) -> bool:
    client = await get_redis()
    if client is None:
        return False
    return bool(await client.exists(key))
