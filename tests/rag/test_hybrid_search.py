import pytest

from app.database.connection import AsyncSessionLocal
from app.rag.ingestion import ingest_document
from app.rag.hybrid_search import hybrid_search


@pytest.mark.asyncio
async def test_hybrid_search():
    async with AsyncSessionLocal() as session:
        await ingest_document(
            session=session,
            filename="hybrid_test.txt",
            content=(
                "AegisAI uses multi-agent orchestration and advanced RAG. "
                * 50
            ),
            content_type="text/plain",
        )

        results = await hybrid_search(
            session=session,
            query="advanced RAG",
            top_k=3,
        )

        assert len(results) > 0
        assert any("advanced RAG" in chunk.content for chunk in results)