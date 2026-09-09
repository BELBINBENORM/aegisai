from app.agents.agent import Agent
from app.agents.state import AgentState
from app.agents.tool import Tool


class ResearchAgent:
    def __init__(
        self,
        agent: Agent | None = None,
    ) -> None:
        self.agent = agent or Agent()

    async def run(
        self,
        query: str,
        tools: list[Tool],
    ) -> AgentState:
        return await self.agent.run(
            query=query,
            tools=tools,
        )