import pytest

from app.database.connection import AsyncSessionLocal
from app.memory.models import Memory
from app.memory.sqlalchemy_store import SQLAlchemyMemoryStore


@pytest.mark.asyncio
async def test_sqlalchemy_memory_store_save_and_get():
    store = SQLAlchemyMemoryStore(AsyncSessionLocal)

    memory = Memory(
        id="memory-test-1",
        user_id="1",
        content="User likes Python.",
        metadata={"source": "test"},
        created_at=__import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ),
    )

    await store.save(memory)

    result = await store.get("memory-test-1")

    assert result is not None
    assert result.id == memory.id
    assert result.user_id == memory.user_id
    assert result.content == memory.content
    assert result.metadata == memory.metadata

    # cleanup
    async with AsyncSessionLocal() as session:
        from app.database.models.memory import Memory as MemoryModel

        model = await session.get(MemoryModel, "memory-test-1")
        if model:
            await session.delete(model)
            await session.commit()


@pytest.mark.asyncio
async def test_sqlalchemy_memory_store_list():
    store = SQLAlchemyMemoryStore(AsyncSessionLocal)

    memory1 = Memory(
        id="memory-test-2",
        user_id="1",
        content="User likes Python.",
        metadata={},
        created_at=__import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ),
    )

    memory2 = Memory(
        id="memory-test-3",
        user_id="1",
        content="User likes AI.",
        metadata={},
        created_at=__import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ),
    )

    await store.save(memory1)
    await store.save(memory2)

    result = await store.list("1")

    assert len(result) >= 2
    assert any(m.id == "memory-test-2" for m in result)
    assert any(m.id == "memory-test-3" for m in result)

    async with AsyncSessionLocal() as session:
        from app.database.models.memory import Memory as MemoryModel

        for memory_id in ["memory-test-2", "memory-test-3"]:
            model = await session.get(MemoryModel, memory_id)
            if model:
                await session.delete(model)
        await session.commit()


@pytest.mark.asyncio
async def test_sqlalchemy_memory_store_search():
    store = SQLAlchemyMemoryStore(AsyncSessionLocal)

    memory = Memory(
        id="memory-test-4",
        user_id="1",
        content="User prefers concise Python answers.",
        metadata={},
        created_at=__import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ),
    )

    await store.save(memory)

    result = await store.search("1", "Python")

    assert any(m.id == "memory-test-4" for m in result)

    async with AsyncSessionLocal() as session:
        from app.database.models.memory import Memory as MemoryModel

        model = await session.get(MemoryModel, "memory-test-4")
        if model:
            await session.delete(model)
            await session.commit()