import pytest
from sqlalchemy import select

from app.database.connection import AsyncSessionLocal
from app.database.models import Document, DocumentChunk
from app.rag.ingestion import ingest_document


@pytest.mark.asyncio
async def test_ingest_document():
    async with AsyncSessionLocal() as session:
        document = await ingest_document(
            session=session,
            filename="test.txt",
            content="AegisAI is a multi-agent AI system. " * 100,
            content_type="text/plain",
        )

        result = await session.execute(
            select(DocumentChunk).where(
                DocumentChunk.document_id == document.id
            )
        )

        chunks = result.scalars().all()

        assert document.filename == "test.txt"
        assert len(chunks) > 0
        assert all(chunk.embedding is not None for chunk in chunks)