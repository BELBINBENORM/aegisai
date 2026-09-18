from app.llm.structured import StructuredLLMClient
from pydantic import BaseModel


class QueryVariants(BaseModel):
    queries: list[str]


class MultiQueryGenerator:
    def __init__(
        self,
        llm_client: StructuredLLMClient | None = None,
    ) -> None:
        self.llm_client = llm_client or StructuredLLMClient()

    async def generate(self, query: str, count: int = 3) -> list[str]:
        prompt = f"""
Generate {count} different search queries for retrieving documents
relevant to the user's question.

Keep each query concise and preserve the original intent.

User question:
{query}
"""

        result = await self.llm_client.generate(
            prompt=prompt,
            response_schema=QueryVariants,
        )

        return result.queries[:count]