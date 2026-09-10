from dataclasses import dataclass, field

from app.memory.models import Memory


@dataclass
class MemoryContext:
    memories: list[Memory] = field(default_factory=list)
    max_memories: int = 10

    def add(self, memory: Memory) -> None:
        self.memories.append(memory)

        if len(self.memories) > self.max_memories:
            self.memories = self.memories[-self.max_memories:]

    def contents(self) -> list[str]:
        return [memory.content for memory in self.memories]

    def clear(self) -> None:
        self.memories.clear()