from datetime import datetime

import pytest

from app.memory.local_store import LocalMemoryStore
from app.memory.models import Memory


@pytest.mark.asyncio
async def test_save_and_get_memory():
    store = LocalMemoryStore()

    memory = Memory(
        id="memory-1",
        user_id="user-1",
        content="User prefers concise answers.",
        metadata={"type": "preference"},
        created_at=datetime.now(),
    )

    await store.save(memory)

    result = await store.get("memory-1")

    assert result == memory


@pytest.mark.asyncio
async def test_get_missing_memory():
    store = LocalMemoryStore()

    result = await store.get("missing")

    assert result is None


@pytest.mark.asyncio
async def test_list_memories_by_user():
    store = LocalMemoryStore()

    memory1 = Memory(
        id="memory-1",
        user_id="user-1",
        content="Memory one",
        metadata={},
        created_at=datetime.now(),
    )

    memory2 = Memory(
        id="memory-2",
        user_id="user-2",
        content="Memory two",
        metadata={},
        created_at=datetime.now(),
    )

    await store.save(memory1)
    await store.save(memory2)

    result = await store.list("user-1")

    assert result == [memory1]