"""
TDD 测试基础设施配置

提供：
- 异步 TestClient (httpx.AsyncClient)
- 内存数据库/SQLite 测试会话
- Redis mock (fakeredis)
- 测试数据工厂（测试用户 seed）
"""

import os
from typing import AsyncGenerator

import fakeredis.aioredis
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# =============================================================================
# 环境隔离（必须在任何 app 模块导入前执行）
# =============================================================================

os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["SECRET_KEY"] = "test-secret-key-only-for-tdd"
os.environ["TOKEN_EXPIRE_SECONDS"] = "3600"

from app.config import Settings
from app import config as config_module

config_module.settings = Settings(
    app_env="testing",
    database_url="sqlite+aiosqlite:///:memory:",
    redis_url="redis://localhost:6379/15",
    secret_key="test-secret-key-only-for-tdd",
    token_expire_seconds=3600,
    address_api_mock_on_failure=True,
)

from app.database import Base, get_db
from app.main import app
from app.models import User


# =============================================================================
# 数据库 fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """创建异步内存数据库引擎，并在测试会话结束后销毁。"""
    from app.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """每个测试函数独立的 DB 会话，自动回滚，保证测试隔离。"""
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


# =============================================================================
# Redis fixtures
# =============================================================================

@pytest_asyncio.fixture
async def redis_client():
    """提供 fakeredis 异步客户端。"""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.aclose()


# =============================================================================
# FastAPI TestClient
# =============================================================================

@pytest_asyncio.fixture
async def client(db_session, redis_client) -> AsyncGenerator[AsyncClient, None]:
    """
    提供基于 httpx.AsyncClient 的异步测试客户端。
    自动注入测试用的 db_session 和 redis_client 到 app 的依赖中。
    """
    from app.core import redis as redis_module

    async def override_get_db():
        yield db_session

    async def override_get_redis():
        yield redis_client

    app.dependency_overrides[get_db] = override_get_db
    redis_module.redis_client = redis_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


# =============================================================================
# 测试数据工厂 fixtures
# =============================================================================

@pytest_asyncio.fixture
async def test_user(db_session):
    """
    在数据库中预置一个标准测试用户，用于登录/鉴权测试。
    账号: test / 密码: 123456 / 昵称: TestUser
    """
    from sqlalchemy import select
    from app.core.security import hash_password

    result = await db_session.execute(select(User).where(User.account == "test"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(account="test", pwd=hash_password("123456"), name="TestUser")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    return {
        "id": user.id,
        "account": user.account,
        "plain_pwd": "123456",
        "name": user.name,
        "pwd": user.pwd,
    }


@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    """
    先调用登录接口获取 token，再返回包含 Authorization Header 的字典。
    用于需要鉴权的接口测试。
    """
    resp = await client.post("/api/v1/auth/login", json={
        "account": test_user["account"],
        "pwd": test_user["plain_pwd"]
    })
    assert resp.status_code == 200
    token = resp.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}
