from fastapi import Depends

from app.core.security import get_current_user
from app.core.rate_limiter import rate_limiter_dependency
from app.core.session import touch_session
from app.schemas.auth import UserInDB


# async def get_active_user(user: UserInDB = Depends(get_current_user)) -> UserInDB:
#     # could add more checks here later
#     return user


async def with_rate_limit(
    # user: UserInDB = Depends(get_active_user),
    user: UserInDB = Depends(get_current_user),
    _rl: bool = Depends(rate_limiter_dependency),
) -> UserInDB:
    """
    Combines: authenticated user + rate limit check + session touch.
    Returns the current user for use in endpoints.
    """
    touch_session(user.username)
    return user
