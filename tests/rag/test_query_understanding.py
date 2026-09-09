import pytest

from app.rag.query_understanding import QueryUnderstanding


@pytest.mark.asyncio
async def test_query_understanding():
    analyzer = QueryUnderstanding()

    result = await analyzer.analyze(
        "What does AegisAI use for storing vector embeddings?"
    )

    assert result.query
    assert result.keywords
    assert isinstance(result.needs_rewrite, bool)