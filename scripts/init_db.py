import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.database import AsyncSessionLocal, Base, engine
from app.models import User


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.account == "test"))
        existing = result.scalar_one_or_none()
        if existing:
            print("User test already exists, skipping.")
            return

        user = User(account="test", pwd=hash_password("123456"), name="TestUser")
        session.add(user)
        await session.commit()
        print(f"Created user: {user.account}")


if __name__ == "__main__":
    asyncio.run(seed())
