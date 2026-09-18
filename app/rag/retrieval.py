from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Document, DocumentChunk
from app.rag.embeddings import generate_embedding
from app.rag.embedding_cache import get_embedding


async def retrieve_chunks(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
    metadata_filter: dict | None = None,
) -> list[DocumentChunk]:
    query_embedding = await get_embedding(query)
    
    statement = (
        select(DocumentChunk).options(selectinload(DocumentChunk.document))
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
class Retriever:
    async def hybrid_search(self, session: AsyncSession, session_id: int, query: str, limit: int = 6, metadata_filter: dict | None = None):
        from app.rag.hybrid_search import hybrid_search
        return await hybrid_search(session=session, query=query, top_k=limit, metadata_filter=metadata_filter)
