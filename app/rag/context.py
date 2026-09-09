from app.database.models import DocumentChunk


def compress_context(
    chunks: list[DocumentChunk],
    max_chars: int = 6000,
) -> str:
    parts = []
    total = 0

    for chunk in chunks:
        content = chunk.content.strip()

        if not content:
            continue

        remaining = max_chars - total

        if remaining <= 0:
            break

        if len(content) > remaining:
            content = content[:remaining]

        parts.append(content)
        total += len(content)

    return "\n\n".join(parts)