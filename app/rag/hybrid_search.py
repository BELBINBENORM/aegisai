from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DocumentChunk
from app.rag.embeddings import generate_embedding
from app.rag.retrieval import retrieve_chunks


async def hybrid_search(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
    metadata_filter: dict | None = None
) -> list[DocumentChunk]:
    # Vector search
    vector_chunks = await retrieve_chunks(
        session=session,
        query=query,
        top_k=top_k,
        metadata_filter=metadata_filter,
    )

    # PostgreSQL full-text search
    search_vector = func.to_tsvector("english", DocumentChunk.content)
    search_query = func.plainto_tsquery("english", query)

    keyword_statement = (
        select(DocumentChunk)
        .where(search_vector.op("@@")(search_query))
        .order_by(
            func.ts_rank(search_vector, search_query).desc()
        )
        .limit(top_k)
    )

    result = await session.execute(keyword_statement)
    keyword_chunks = list(result.scalars().all())

    # Combine results while removing duplicates
    combined = []
    seen_ids = set()

    for chunk in vector_chunks + keyword_chunks:
        if chunk.id not in seen_ids:
            combined.append(chunk)
            seen_ids.add(chunk.id)

    return combined[:top_k]