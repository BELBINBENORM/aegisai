import pytest

from app.rag.embeddings import generate_embedding


@pytest.mark.asyncio
async def test_generate_embedding():
    embedding = await generate_embedding("AegisAI test document")

    assert isinstance(embedding, list)
    assert len(embedding) == 768