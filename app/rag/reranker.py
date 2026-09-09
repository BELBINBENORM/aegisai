from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.database.models import DocumentChunk


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    return CrossEncoder(MODEL_NAME)


def rerank_chunks(
    query: str,
    chunks: list[DocumentChunk],
    top_k: int = 5,
) -> list[DocumentChunk]:
    if not chunks:
        return []

    model = get_reranker()

    pairs = [
        (query, chunk.content)
        for chunk in chunks
    ]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(chunks, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    return [
        chunk
        for chunk, _ in ranked[:top_k]
    ]