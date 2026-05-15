"""
TDD 测试基础设施配置

提供：
- 异步 TestClient (httpx.AsyncClient)
- 内存数据库/SQLite 测试会话
- Redis mock (fakeredis)
- 测试数据工厂（测试用户 seed）
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 被测应用入口（后续开发时替换为真实路径）
# from app.main import app
# from app.database import Base, get_db
# from app.core.security import hash_password
# from app.models import User

# =============================================================================
# 环境隔离
# =============================================================================

os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("SECRET_KEY", "test-secret-key-only-for-tdd")
os.environ.setdefault("TOKEN_EXPIRE_SECONDS", "3600")


# =============================================================================
# 事件循环（pytest-asyncio 兼容）
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """为整个测试会话创建一个事件循环。"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# 数据库 fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """
    创建异步内存数据库引擎，并在测试会话结束后销毁。
    对应开发目标：app/database.py 中的引擎创建逻辑。
    """
    # TODO: 开发完成后替换为真实导入
    # from app.database import Base
    # engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    # yield engine
    # await engine.dispose()
    pass


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    每个测试函数独立的 DB 会话，自动回滚，保证测试隔离。
    对应开发目标：app/database.py 中的 get_db / AsyncSessionLocal。
    """
    # TODO: 开发完成后替换为真实导入
    # async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    # async with async_session() as session:
    #     yield session
    #     await session.rollback()
    pass


# =============================================================================
# Redis fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="session")
async def redis_client():
    """
    提供 Redis 客户端（测试环境使用 fakeredis 或真实 Redis 的空闲 DB）。
    对应开发目标：app/core/redis.py 中的 redis_client。
    """
    # TODO: 开发完成后替换为真实导入
    # from app.core.redis import get_redis
    # client = get_redis()
    # yield client
    # await client.flushdb()  # 测试结束后清空
    pass


# =============================================================================
# FastAPI TestClient
# =============================================================================

@pytest_asyncio.fixture
async def client(db_session, redis_client) -> AsyncGenerator[AsyncClient, None]:
    """
    提供基于 httpx.AsyncClient 的异步测试客户端。
    自动注入测试用的 db_session 和 redis_client 到 app 的依赖中。

    对应开发目标：
    - app/main.py 中的 FastAPI app 实例
    - app/deps.py 中的 get_db / get_redis 依赖替换
    """
    # TODO: 开发完成后替换为真实导入
    # from app.main import app
    # from app.deps import get_db, get_redis
    #
    # async def override_get_db():
    #     yield db_session
    #
    # async def override_get_redis():
    #     yield redis_client
    #
    # app.dependency_overrides[get_db] = override_get_db
    # app.dependency_overrides[get_redis] = override_get_redis
    #
    # transport = ASGITransport(app=app)
    # async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
    #     yield ac
    #
    # app.dependency_overrides.clear()
    pass


# =============================================================================
# 测试数据工厂 fixtures
# =============================================================================

@pytest_asyncio.fixture
async def test_user(db_session):
    """
    在数据库中预置一个标准测试用户，用于登录/鉴权测试。
    账号: test / 密码: 123456 / 昵称: TestUser

    对应开发目标：app/models.py User 模型 + app/core/security.py hash_password。
    """
    # TODO: 开发完成后替换为真实导入
    # from app.core.security import hash_password
    # from app.models import User
    #
    # user = User(account="test", pwd=hash_password("123456"), name="TestUser")
    # db_session.add(user)
    # await db_session.commit()
    # await db_session.refresh(user)
    # return {"id": user.id, "account": user.account, "plain_pwd": "123456", "name": user.name}
    pass


@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    """
    先调用登录接口获取 token，再返回包含 Authorization Header 的字典。
    用于需要鉴权的接口测试。
    """
    # TODO: 开发完成后替换为真实调用
    # resp = await client.post("/api/v1/auth/login", json={
    #     "account": test_user["account"],
    #     "pwd": test_user["plain_pwd"]
    # })
    # assert resp.status_code == 200
    # token = resp.json()["data"]["token"]
    # return {"Authorization": f"Bearer {token}"}
    pass
