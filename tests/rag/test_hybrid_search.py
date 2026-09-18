import pytest

from app.database.connection import AsyncSessionLocal
from app.rag.ingestion import ingest_document
from app.rag.hybrid_search import hybrid_search


@pytest.mark.asyncio
async def test_hybrid_search_respects_metadata_filter():
    async with AsyncSessionLocal() as session:

        await ingest_document(
            session=session,
            filename="allowed.txt",
            content="AegisAI advanced RAG allowed document.",
            content_type="text/plain",
            document_metadata={"category": "allowed"},
        )

        blocked_document = await ingest_document(
            session=session,
            filename="blocked.txt",
            content="AegisAI advanced RAG blocked document.",
            content_type="text/plain",
            document_metadata={"category": "blocked"},
        )

        results = await hybrid_search(
            session=session,
            query="advanced RAG",
            top_k=10,
            metadata_filter={"category": "allowed"},
        )

        assert len(results) > 0

        for chunk in results:
            assert chunk.document_id != blocked_document.id