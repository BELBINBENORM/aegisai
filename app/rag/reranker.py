import re
from app.database.models import DocumentChunk


def _terms(text: str) -> set[str]:
    return set(re.findall(r"\b\w+\b", text.lower()))


def rerank_chunks(query: str, chunks: list[DocumentChunk], top_k: int = 5) -> list[DocumentChunk]:
    if not chunks or top_k <= 0:
        return []
    query_terms = _terms(query)
    scored = []
    for index, chunk in enumerate(chunks):
        terms = _terms(chunk.content)
        overlap = len(query_terms & terms)
        phrase_bonus = 1 if query.lower() in chunk.content.lower() else 0
        scored.append((overlap + phrase_bonus, -index, chunk))
    scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
    return [chunk for _, _, chunk in scored[:top_k]]
