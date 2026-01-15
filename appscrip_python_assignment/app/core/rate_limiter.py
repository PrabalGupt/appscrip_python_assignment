import time
from typing import Dict

from fastapi import HTTPException, status, Depends

from app.config import settings
from app.core.security import get_current_user
from app.schemas.auth import UserInDB

# key: username, value: {tokens, last_refill}
_buckets: Dict[str, Dict[str, float]] = {}


def _get_bucket_for(user_id: str) -> Dict[str, float]:
    now = time.time()
    bucket = _buckets.get(user_id)
    if bucket is None:
        bucket = {"tokens": float(settings.rate_limit_requests), "last_refill": now}
        _buckets[user_id] = bucket
        return bucket

    # refill tokens
    elapsed = now - bucket["last_refill"]
    if elapsed > 0:
        refill_rate = (
            settings.rate_limit_requests / settings.rate_limit_window_seconds
        )  # tokens per second
        new_tokens = bucket["tokens"] + elapsed * refill_rate
        bucket["tokens"] = min(float(settings.rate_limit_requests), new_tokens)
        bucket["last_refill"] = now

    return bucket


async def rate_limiter_dependency(current_user: UserInDB = Depends(get_current_user)):
    user_id = current_user.username
    bucket = _get_bucket_for(user_id)

    if bucket["tokens"] < 1.0:
        # no tokens left
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )

    bucket["tokens"] -= 1.0
    _buckets[user_id] = bucket
    return True
