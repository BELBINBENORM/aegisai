import re

from app.database.models import DocumentChunk


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\b\w+\b", text.lower()))


def rerank_chunks(
    query: str,
    chunks: list[DocumentChunk],
    top_k: int = 5,
) -> list[DocumentChunk]:
    query_tokens = _tokens(query)

    def score(chunk: DocumentChunk) -> float:
        content = chunk.content.lower()
        content_tokens = _tokens(content)

        if not query_tokens:
            return 0.0

        overlap = len(query_tokens & content_tokens) / len(query_tokens)

        phrase_bonus = 1.0 if query.lower() in content else 0.0

        return overlap + phrase_bonus

    ranked = sorted(chunks, key=score, reverse=True)

    return ranked[:top_k]