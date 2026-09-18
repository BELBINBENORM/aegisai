import json
import hashlib
from app.cache.cache import get_cached, set_cached
from app.rag.embeddings import generate_embedding

async def get_embedding(text: str) -> list[float]:
    key = 'embedding:' + hashlib.sha256(text.encode('utf-8')).hexdigest()
    cached = await get_cached(key)
    if cached is not None:
        if isinstance(cached, str):
            try:
                cached = json.loads(cached)
            except json.JSONDecodeError:
                return [float(x) for x in cached.split(',') if x.strip()]
        return list(cached)
    embedding = await generate_embedding(text)
    await set_cached(key, embedding, expire=86400)
    return embedding
