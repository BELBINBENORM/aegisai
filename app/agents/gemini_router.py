from app.agents.router import AgentRouter
from app.llm.structured import StructuredLLMClient
from pydantic import BaseModel


class RouteDecision(BaseModel):
    agent: str


class GeminiAgentRouter(AgentRouter):
    def __init__(
        self,
        client: StructuredLLMClient | None = None,
    ) -> None:
        self.client = client or StructuredLLMClient()

    async def route(self, query: str) -> str:
        prompt = f"""
Choose the best agent for this user query.

Available agents:
- rag
- research
- tool
- verification

User query:
{query}

Return only the selected agent.
"""

        result = await self.client.generate(
            prompt=prompt,
            response_schema=RouteDecision,
        )

        return result.agent