from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document, DocumentChunk
from app.rag.retrieval import retrieve_chunks


async def hybrid_search(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
    metadata_filter: dict | None = None,
) -> list[DocumentChunk]:

    candidate_k = max(top_k * 3, 10)

    vector_chunks = await retrieve_chunks(
        session=session,
        query=query,
        top_k=candidate_k,
        metadata_filter=metadata_filter,
    )

    search_vector = func.to_tsvector(
        "english",
        DocumentChunk.content,
    )

    search_query = func.plainto_tsquery(
        "english",
        query,
    )

    keyword_statement = (
        select(DocumentChunk)
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(
            search_vector.op("@@")(search_query)
        )
    )

    if metadata_filter:
        for key, value in metadata_filter.items():
            keyword_statement = keyword_statement.where(
                Document.document_metadata[key].as_string()
                == str(value)
            )

    keyword_statement = (
        keyword_statement
        .order_by(
            func.ts_rank(
                search_vector,
                search_query,
            ).desc()
        )
        .limit(candidate_k)
    )

    result = await session.execute(keyword_statement)
    keyword_chunks = list(result.scalars().all())

    rrf_constant = 60

    scores = {}
    chunks_by_id = {}

    for rank, chunk in enumerate(vector_chunks, start=1):
        chunks_by_id[chunk.id] = chunk

        score = 1 / (rrf_constant + rank)
        scores[chunk.id] = scores.get(chunk.id, 0) + score

    for rank, chunk in enumerate(keyword_chunks, start=1):
        chunks_by_id[chunk.id] = chunk

        score = 1 / (rrf_constant + rank)
        scores[chunk.id] = scores.get(chunk.id, 0) + score

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    return [
        chunks_by_id[chunk_id]
        for chunk_id in ranked_ids[:top_k]
    ]