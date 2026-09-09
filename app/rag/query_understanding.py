from pydantic import BaseModel

from app.llm.structured import StructuredLLMClient


class QueryAnalysis(BaseModel):
    query: str
    keywords: list[str]
    needs_rewrite: bool


class QueryUnderstanding:
    def __init__(
        self,
        llm_client: StructuredLLMClient | None = None,
    ) -> None:
        self.llm_client = llm_client or StructuredLLMClient()

    async def analyze(self, query: str) -> QueryAnalysis:
        prompt = f"""
Analyze the following user query for document retrieval.

Extract the important search keywords and determine whether
the query should be rewritten before retrieval.

User query:
{query}
"""

        return await self.llm_client.generate(
            prompt=prompt,
            response_schema=QueryAnalysis,
        )