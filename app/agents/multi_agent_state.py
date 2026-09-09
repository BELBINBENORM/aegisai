from dataclasses import dataclass, field
from typing import Any


@dataclass
class MultiAgentState:
    query: str
    agent_results: dict[str, list[Any]] = field(default_factory=dict)
    current_agent: str | None = None
    completed_agents: list[str] = field(default_factory=list)
    error: str | None = None

    def add_result(self, agent_name: str, result: Any) -> None:
        if agent_name not in self.agent_results:
            self.agent_results[agent_name] = []

        self.agent_results[agent_name].append(result)

        if agent_name not in self.completed_agents:
            self.completed_agents.append(agent_name)

    def set_current_agent(self, agent_name: str) -> None:
        self.current_agent = agent_name