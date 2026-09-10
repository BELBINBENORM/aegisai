from datetime import datetime

from app.memory.context import MemoryContext
from app.memory.models import Memory


def test_memory_context_adds_memory():
    context = MemoryContext()

    memory = Memory(
        id="memory-1",
        user_id="user-1",
        content="User prefers concise answers.",
        metadata={},
        created_at=datetime.now(),
    )

    context.add(memory)

    assert context.memories == [memory]


def test_memory_context_returns_contents():
    context = MemoryContext()

    context.add(
        Memory(
            id="memory-1",
            user_id="user-1",
            content="User likes Python.",
            metadata={},
            created_at=datetime.now(),
        )
    )

    context.add(
        Memory(
            id="memory-2",
            user_id="user-1",
            content="User prefers concise answers.",
            metadata={},
            created_at=datetime.now(),
        )
    )

    assert context.contents() == [
        "User likes Python.",
        "User prefers concise answers.",
    ]