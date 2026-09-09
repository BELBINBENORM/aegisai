from app.database.models import DocumentChunk
from app.rag.context import compress_context


def test_compress_context():
    chunks = [
        DocumentChunk(content="AegisAI uses advanced RAG.", document_id=1),
        DocumentChunk(content="AegisAI uses multiple agents.", document_id=1),
    ]

    context = compress_context(chunks)

    assert "advanced RAG" in context
    assert "multiple agents" in context