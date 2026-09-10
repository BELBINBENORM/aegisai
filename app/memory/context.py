from dataclasses import dataclass, field

from app.memory.models import Memory


@dataclass
class MemoryContext:
    memories: list[Memory] = field(default_factory=list)

    def add(self, memory: Memory) -> None:
        self.memories.append(memory)

    def contents(self) -> list[str]:
        return [memory.content for memory in self.memories]