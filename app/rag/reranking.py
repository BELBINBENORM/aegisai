from app.database.models import DocumentChunk


def rerank_chunks(
    query: str,
    chunks: list[DocumentChunk],
    top_k: int = 5,
) -> list[DocumentChunk]:
    query_terms = set(query.lower().split())

    def score(chunk: DocumentChunk) -> int:
        content_terms = set(chunk.content.lower().split())
        return len(query_terms & content_terms)

    ranked = sorted(chunks, key=score, reverse=True)

    return ranked[:top_k]