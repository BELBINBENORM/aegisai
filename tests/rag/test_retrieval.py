import pytest
from sqlalchemy import select

from app.database.connection import AsyncSessionLocal
from app.database.models import DocumentChunk
from app.rag.ingestion import ingest_document
from app.rag.retrieval import retrieve_chunks


@pytest.mark.asyncio
async def test_retrieve_chunks():
    async with AsyncSessionLocal() as session:
        await ingest_document(
            session=session,
            filename="retrieval_test.txt",
            content=(
                "AegisAI uses multi-agent orchestration and advanced RAG. "
                * 50
            ),
            content_type="text/plain",
        )

        chunks = await retrieve_chunks(
            session=session,
            query="How does AegisAI use advanced RAG?",
            top_k=3,
        )

        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)