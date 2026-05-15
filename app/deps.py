from fastapi import Header, Request
from fastapi.param_functions import Depends

from app.config import settings
from app.core import redis as redis_module
from app.core.exceptions import BizException
from app.core.whitelist import is_whitelisted
from app.database import AsyncSessionLocal


async def get_redis():
    yield redis_module.redis_client


async def get_current_user(request: Request, authorization: str = Header(None)) -> str:
    if is_whitelisted(request.url.path):
        return ""

    if not authorization or not authorization.startswith("Bearer "):
        raise BizException(code=401, msg="未授权，缺少有效Token")

    token = authorization[7:]
    user_id = await redis_module.redis_client.get(f"token:{token}")
    if not user_id:
        raise BizException(code=401, msg="Token已过期或无效")

    return user_id
