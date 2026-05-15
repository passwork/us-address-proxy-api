import asyncio

from app.config import settings
from app.core.security import hash_password
from app.database import AsyncSessionLocal
from app.models import User


async def seed():
    async with AsyncSessionLocal() as session:
        user = User(account="test", pwd=hash_password("123456"), name="TestUser")
        session.add(user)
        await session.commit()
        print(f"Created user: {user.account}")


if __name__ == "__main__":
    asyncio.run(seed())
