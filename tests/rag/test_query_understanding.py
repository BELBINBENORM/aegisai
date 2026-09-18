import pytest

from app.rag.query_understanding import (
    QueryAnalysis,
    QueryUnderstanding,
)
from app.llm.structured import StructuredLLMClient


@pytest.mark.asyncio
async def test_query_understanding(monkeypatch):
    async def mock_generate(self, prompt, response_schema, model="gemini-3.6-flash"):
        return QueryAnalysis(
            query="What does AegisAI use for storing vector embeddings?",
            keywords=["AegisAI", "vector", "embeddings"],
            needs_rewrite=True,
        )

    monkeypatch.setattr(
        StructuredLLMClient,
        "generate",
        mock_generate,
    )

    analyzer = QueryUnderstanding()

    result = await analyzer.analyze(
        "What does AegisAI use for storing vector embeddings?"
    )

    assert result.query
    assert result.keywords
    assert isinstance(result.needs_rewrite, bool)