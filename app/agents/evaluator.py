from pydantic import BaseModel

from app.llm.structured import StructuredLLMClient


class Evaluation(BaseModel):
    sufficient: bool
    reason: str


class AgentEvaluator:
    def __init__(
        self,
        client: StructuredLLMClient | None = None,
    ) -> None:
        self.client = client or StructuredLLMClient()

    async def evaluate(
        self,
        query: str,
        result: object,
    ) -> Evaluation:
        prompt = f"""
Evaluate whether the agent result is sufficient to answer the user request.

User request:
{query}

Agent result:
{result}

Return:
- sufficient=true if the result adequately answers the request
- sufficient=false if more work is needed
- reason explaining the decision briefly
"""

        return await self.client.generate(
            prompt=prompt,
            response_schema=Evaluation,
        )