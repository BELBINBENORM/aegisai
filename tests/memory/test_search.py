from datetime import datetime

import pytest

from app.memory.local_store import LocalMemoryStore
from app.memory.models import Memory


@pytest.mark.asyncio
async def test_search_memories_by_content():
    store = LocalMemoryStore()

    memory1 = Memory(
        id="memory-1",
        user_id="user-1",
        content="User prefers concise answers.",
        metadata={},
        created_at=datetime.now(),
    )

    memory2 = Memory(
        id="memory-2",
        user_id="user-1",
        content="User likes Python.",
        metadata={},
        created_at=datetime.now(),
    )

    await store.save(memory1)
    await store.save(memory2)

    result = await store.search("user-1", "concise")

    assert result == [memory1]


@pytest.mark.asyncio
async def test_search_is_case_insensitive():
    store = LocalMemoryStore()

    memory = Memory(
        id="memory-1",
        user_id="user-1",
        content="User prefers Python.",
        metadata={},
        created_at=datetime.now(),
    )

    await store.save(memory)

    result = await store.search("user-1", "PYTHON")

    assert result == [memory]


@pytest.mark.asyncio
async def test_search_only_returns_user_memories():
    store = LocalMemoryStore()

    memory = Memory(
        id="memory-1",
        user_id="user-2",
        content="User prefers concise answers.",
        metadata={},
        created_at=datetime.now(),
    )

    await store.save(memory)

    result = await store.search("user-1", "concise")

    assert result == []