from pydantic import BaseModel

from app.llm.structured import StructuredLLMClient


class RewrittenQuery(BaseModel):
    query: str


class QueryRewriter:
    def __init__(self, llm_client: StructuredLLMClient | None = None) -> None:
        self.llm_client = llm_client or StructuredLLMClient()

    async def rewrite(self, query: str) -> str:
        prompt = f"""
Rewrite this user query into a clear, concise search query.

Return only the rewritten search query.

User query:
{query}
"""

        result = await self.llm_client.generate(
            prompt=prompt,
            response_schema=RewrittenQuery,
        )

        return result.query.strip()