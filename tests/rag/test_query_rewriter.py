import pytest

from app.rag.query_rewriter import QueryRewriter, RewrittenQuery
from app.llm.structured import StructuredLLMClient


@pytest.mark.asyncio
async def test_query_rewriter(monkeypatch):
    async def mock_generate(self, prompt, response_schema, model="gemini-3.6-flash"):
        return RewrittenQuery(
            query="AegisAI vector embedding storage"
        )

    monkeypatch.setattr(
        StructuredLLMClient,
        "generate",
        mock_generate,
    )

    rewriter = QueryRewriter()

    result = await rewriter.rewrite(
        "What does AegisAI use for storing vector embeddings?"
    )

    assert result
    assert isinstance(result, str)