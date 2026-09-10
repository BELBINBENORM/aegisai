from datetime import datetime, timezone

from app.memory.context import MemoryContext
from app.memory.models import Memory


def make_memory(number: int) -> Memory:
    return Memory(
        id=f"memory-{number}",
        user_id="1",
        content=f"Memory {number}",
        metadata={},
        created_at=datetime.now(timezone.utc),
    )


def test_memory_context_keeps_recent_memories():
    context = MemoryContext(max_memories=3)

    for number in range(1, 6):
        context.add(make_memory(number))

    assert len(context.memories) == 3
    assert context.contents() == [
        "Memory 3",
        "Memory 4",
        "Memory 5",
    ]


def test_memory_context_can_be_cleared():
    context = MemoryContext()

    context.add(make_memory(1))
    context.add(make_memory(2))

    context.clear()

    assert context.memories == []
    assert context.contents() == []