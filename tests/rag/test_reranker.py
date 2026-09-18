from app.database.models import DocumentChunk
from app.rag.reranker import rerank_chunks


def test_rerank_chunks():
    chunks = [
        DocumentChunk(
            content="Python is a programming language.",
            document_id=1,
        ),
        DocumentChunk(
            content="AegisAI uses advanced RAG and multi-agent orchestration.",
            document_id=1,
        ),
        DocumentChunk(
            content="Machine learning models process data.",
            document_id=1,
        ),
    ]

    results = rerank_chunks(
        query="AegisAI advanced RAG",
        chunks=chunks,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].content.startswith("AegisAI")