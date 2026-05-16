from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core import redis as redis_module
from app.core.exceptions import BizException
from app.core.whitelist import is_whitelisted

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if is_whitelisted(request.url.path):
        return ""

    if not credentials or credentials.scheme != "Bearer":
        raise BizException(code=401, msg="未授权，缺少有效Token")

    user_id = await redis_module.redis_client.get(f"token:{credentials.credentials}")
    if not user_id:
        raise BizException(code=401, msg="Token已过期或无效")

    return user_id
