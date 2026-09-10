import pytest

from app.database.connection import AsyncSessionLocal
from app.database.models.user import User


@pytest.fixture
async def test_user():
    async with AsyncSessionLocal() as session:
        user = await session.get(User, 1)

        if user is None:
            user = User(
                id=1,
                email="memory-test@example.com",
            )
            session.add(user)
            await session.commit()
        else:
            user.email = "memory-test@example.com"
            await session.commit()

        yield user