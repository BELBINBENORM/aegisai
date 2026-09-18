from app.agents.agent import Agent
from app.agents.state import AgentState
from app.agents.tool_provider import ToolProvider
import inspect


class ResearchAgent:
    def __init__(
        self,
        agent: Agent | None = None,
        tool_provider: ToolProvider | None = None,
    ) -> None:
        self.agent = agent or Agent()
        self.tool_provider = tool_provider

    async def run(self, query: str, event_callback=None, request_id: str = "unknown", **kwargs) -> AgentState:
        tools = []

        if self.tool_provider:
            tools = await self.tool_provider.get_tools()

        self.agent.event_callback = event_callback
        call_kwargs = {"query": query, "tools": tools}
        call_kwargs.update(kwargs)
        call_kwargs["request_id"] = request_id
        sig = inspect.signature(self.agent.run)
        accepts_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        )
        if not accepts_kwargs:
            call_kwargs = {k: v for k, v in call_kwargs.items() if k in sig.parameters}
        return await self.agent.run(**call_kwargs)