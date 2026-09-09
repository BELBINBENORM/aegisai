from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document, DocumentChunk
from app.rag.embeddings import generate_embedding


async def retrieve_chunks(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
    metadata_filter: dict | None = None,
) -> list[DocumentChunk]:
    query_embedding = await generate_embedding(query)

    statement = (
        select(DocumentChunk)
        .join(Document, Document.id == DocumentChunk.document_id)
    )

    if metadata_filter:
        for key, value in metadata_filter.items():
            statement = statement.where(
                Document.document_metadata[key].as_string() == str(value)
            )

    statement = (
        statement
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )

    result = await session.execute(statement)

    return list(result.scalars().all())