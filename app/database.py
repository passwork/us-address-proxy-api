from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

_engine_kwargs = {"echo": False, "future": True}
if settings.database_url.startswith("sqlite"):
    _engine_kwargs.update(
        {
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False},
        }
    )

engine = create_async_engine(settings.database_url, **_engine_kwargs)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
