from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core import redis as redis_module
from app.core.exceptions import BizException
from app.core.security import create_token, verify_password
from app.database import get_db
from app.deps import security
from app.models import User
from app.schemas import BaseResponse, LoginRequest, LoginResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.account == body.account))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.pwd, user.pwd):
        raise BizException(code=400, msg="账号或密码错误")

    token = create_token()
    await redis_module.redis_client.setex(
        f"token:{token}",
        settings.token_expire_seconds,
        str(user.id),
    )

    return LoginResponse(
        code=200,
        data={"token": token, "expires_in": settings.token_expire_seconds},
        msg="success",
    )


@router.post("/logout", response_model=BaseResponse)
async def logout(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if not credentials or credentials.scheme != "Bearer":
        raise BizException(code=401, msg="未授权，缺少有效Token")

    user_id = await redis_module.redis_client.get(f"token:{credentials.credentials}")
    if not user_id:
        raise BizException(code=401, msg="Token已过期或无效")

    await redis_module.redis_client.delete(f"token:{credentials.credentials}")
    return BaseResponse(code=200, data=None, msg="success")
