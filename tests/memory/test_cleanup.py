from datetime import datetime, timedelta, timezone

import pytest
from unittest.mock import AsyncMock, patch

from app.database.connection import AsyncSessionLocal
from app.memory.sqlalchemy_store import SQLAlchemyMemoryStore
from app.memory.local_store import LocalMemoryStore
from app.memory.models import Memory


def make_memory(memory_id: str, created_at: datetime) -> Memory:
    return Memory(
        id=memory_id,
        user_id="1",
        content=f"Memory {memory_id}",
        metadata={},
        created_at=created_at,
    )


@pytest.mark.asyncio
async def test_local_memory_store_delete_older_than():
    store = LocalMemoryStore()

    now = datetime.now(timezone.utc)
    old_memory = make_memory(
        "old",
        now - timedelta(days=10),
    )
    new_memory = make_memory(
        "new",
        now,
    )

    await store.save(old_memory)
    await store.save(new_memory)

    await store.delete_older_than(
        "1",
        now - timedelta(days=5),
    )

    result = await store.list("1")

    assert len(result) == 1
    assert result[0].id == "new"

@pytest.mark.asyncio
async def test_sqlalchemy_memory_store_delete_older_than(test_user):
    store = SQLAlchemyMemoryStore(AsyncSessionLocal)

    now = datetime.now(timezone.utc)

    old_memory = make_memory(
        "cleanup-old",
        now - timedelta(days=10),
    )

    new_memory = make_memory(
        "cleanup-new",
        now,
    )

    try:
        with patch(
            "app.memory.sqlalchemy_store.generate_embedding",
            new=AsyncMock(return_value=[0.1] * 768),
        ):
            await store.save(old_memory)
            await store.save(new_memory)

        await store.delete_older_than(
            str(test_user.id),
            now - timedelta(days=5),
        )

        assert await store.get("cleanup-old") is None
        assert await store.get("cleanup-new") is not None

    finally:
        async with AsyncSessionLocal() as session:
            from app.database.models.memory import Memory as MemoryModel

            for memory_id in ["cleanup-old", "cleanup-new"]:
                model = await session.get(MemoryModel, memory_id)

                if model:
                    await session.delete(model)

            await session.commit()