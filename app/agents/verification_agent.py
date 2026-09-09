from app.agents.agent import Agent
from app.agents.state import AgentState
from app.agents.tool_provider import ToolProvider


class VerificationAgent:
    def __init__(
        self,
        agent: Agent | None = None,
        tool_provider: ToolProvider | None = None,
    ) -> None:
        self.agent = agent or Agent()
        self.tool_provider = tool_provider

    async def run(self, query: str) -> AgentState:
        tools = []

        if self.tool_provider:
            tools = await self.tool_provider.get_tools()

        return await self.agent.run(
            query=query,
            tools=tools,
        )