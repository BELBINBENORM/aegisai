import json

from app.cache.cache import get_cached, set_cached
from app.rag.embeddings import generate_embedding


async def get_embedding(text: str) -> list[float]:
    key = f"embedding:{text}"

    cached = await get_cached(key)

    if cached:
        return json.loads(cached)

    embedding = await generate_embedding(text)

    await set_cached(
        key,
        json.dumps(embedding),
        expire=86400,
    )

    return embedding