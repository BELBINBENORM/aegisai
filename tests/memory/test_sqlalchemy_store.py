from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.database.connection import AsyncSessionLocal
from app.memory.models import Memory
from app.memory.sqlalchemy_store import SQLAlchemyMemoryStore


@pytest.mark.asyncio
async def test_sqlalchemy_memory_store_save_and_get(test_user):
    store = SQLAlchemyMemoryStore(AsyncSessionLocal)

    memory = Memory(
        id="memory-test-1",
        user_id=str(test_user.id),
        content="User likes Python.",
        metadata={"source": "test"},
        created_at=datetime.now(timezone.utc),
    )

    try:
        with patch(
            "app.memory.sqlalchemy_store.generate_embedding",
            new=AsyncMock(return_value=[0.1] * 768),
        ):
            await store.save(memory)

        result = await store.get("memory-test-1")

        assert result is not None
        assert result.id == memory.id
        assert result.user_id == memory.user_id
        assert result.content == memory.content
        assert result.metadata == memory.metadata
        assert result.embedding == [0.1] * 768

    finally:
        async with AsyncSessionLocal() as session:
            from app.database.models.memory import Memory as MemoryModel

            model = await session.get(
                MemoryModel,
                "memory-test-1",
            )

            if model:
                await session.delete(model)
                await session.commit()


@pytest.mark.asyncio
async def test_sqlalchemy_memory_store_list(test_user):
    store = SQLAlchemyMemoryStore(AsyncSessionLocal)

    memory1 = Memory(
        id="memory-test-2",
        user_id=str(test_user.id),
        content="User likes Python.",
        metadata={},
        created_at=datetime.now(timezone.utc),
    )

    memory2 = Memory(
        id="memory-test-3",
        user_id=str(test_user.id),
        content="User likes AI.",
        metadata={},
        created_at=datetime.now(timezone.utc),
    )

    try:
        with patch(
            "app.memory.sqlalchemy_store.generate_embedding",
            new=AsyncMock(return_value=[0.1] * 768),
        ):
            await store.save(memory1)
            await store.save(memory2)

        result = await store.list(test_user.id)

        assert len(result) >= 2
        assert any(
            memory.id == "memory-test-2"
            for memory in result
        )
        assert any(
            memory.id == "memory-test-3"
            for memory in result
        )

    finally:
        async with AsyncSessionLocal() as session:
            from app.database.models.memory import Memory as MemoryModel

            for memory_id in [
                "memory-test-2",
                "memory-test-3",
            ]:
                model = await session.get(
                    MemoryModel,
                    memory_id,
                )

                if model:
                    await session.delete(model)

            await session.commit()


@pytest.mark.asyncio
async def test_sqlalchemy_memory_store_search(test_user):
    store = SQLAlchemyMemoryStore(AsyncSessionLocal)

    memory = Memory(
        id="memory-test-4",
        user_id=str(test_user.id),
        content="User prefers concise Python answers.",
        metadata={},
        created_at=datetime.now(timezone.utc),
    )

    try:
        with patch(
            "app.memory.sqlalchemy_store.generate_embedding",
            new=AsyncMock(return_value=[0.1] * 768),
        ):
            await store.save(memory)

        result = await store.search(
            str(test_user.id),
            "Python",
        )

        assert any(
            item.id == "memory-test-4"
            for item in result
        )

    finally:
        async with AsyncSessionLocal() as session:
            from app.database.models.memory import Memory as MemoryModel

            model = await session.get(
                MemoryModel,
                "memory-test-4",
            )

            if model:
                await session.delete(model)
                await session.commit()