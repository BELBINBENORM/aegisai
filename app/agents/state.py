from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    query: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)

    step_count: int = 0
    max_steps: int = 5

    final_answer: str | None = None
    error: str | None = None

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({
            "role": role,
            "content": content,
        })

    def add_tool_call(self, name: str, arguments: dict[str, Any]) -> None:
        self.tool_calls.append({
            "name": name,
            "arguments": arguments,
        })

    def increment_step(self) -> None:
        self.step_count += 1

    def can_continue(self) -> bool:
        return self.step_count < self.max_steps