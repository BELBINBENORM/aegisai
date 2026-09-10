import pytest

from app.memory.manager import MemoryManager


@pytest.mark.asyncio
async def test_remember_creates_and_saves_memory():
    manager = MemoryManager()

    memory = await manager.remember(
        user_id="user-1",
        content="User prefers concise answers.",
        metadata={"type": "preference"},
    )

    assert memory.user_id == "user-1"
    assert memory.content == "User prefers concise answers."
    assert memory.metadata == {"type": "preference"}

    result = await manager.get(memory.id)

    assert result == memory


@pytest.mark.asyncio
async def test_list_user_memories():
    manager = MemoryManager()

    memory1 = await manager.remember(
        user_id="user-1",
        content="Memory one",
    )

    await manager.remember(
        user_id="user-2",
        content="Memory two",
    )

    result = await manager.list("user-1")

    assert result == [memory1]


@pytest.mark.asyncio
async def test_search_user_memories():
    manager = MemoryManager()

    memory = await manager.remember(
        user_id="user-1",
        content="User prefers concise answers.",
    )

    await manager.remember(
        user_id="user-1",
        content="User likes Python.",
    )

    result = await manager.search("user-1", "concise")

    assert result == [memory]