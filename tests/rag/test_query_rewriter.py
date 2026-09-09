import pytest

from app.rag.query_rewriter import QueryRewriter


@pytest.mark.asyncio
async def test_query_rewriter():
    rewriter = QueryRewriter()

    result = await rewriter.rewrite(
        "What does AegisAI use for storing vector embeddings?"
    )

    assert result
    assert isinstance(result, str)