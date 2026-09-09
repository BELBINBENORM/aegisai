from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DocumentChunk
from app.rag.embeddings import generate_embedding


async def retrieve_chunks(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
) -> list[DocumentChunk]:
    query_embedding = await generate_embedding(query)

    statement = (
        select(DocumentChunk)
        .order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        .limit(top_k)
    )

    result = await session.execute(statement)

    return list(result.scalars().all())