from pydantic import BaseModel

from app.llm.structured import StructuredLLMClient


class Reflection(BaseModel):
    analysis: str
    revised_task: str


class AgentReflector:
    def __init__(
        self,
        client: StructuredLLMClient | None = None,
    ) -> None:
        self.client = client or StructuredLLMClient()

    async def reflect(
        self,
        query: str,
        result: object,
        reason: str,
    ) -> Reflection:
        prompt = f"""
Reflect on an agent result that was judged insufficient.

Original task:
{query}

Agent result:
{result}

Evaluation reason:
{reason}

Identify what is missing or wrong and create a revised task
that should improve the next attempt.

Return:
- analysis: brief explanation of the problem
- revised_task: the improved task
"""

        return await self.client.generate(
            prompt=prompt,
            response_schema=Reflection,
        )