from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document, DocumentChunk
from app.rag.chunking import chunk_text
from app.rag.embeddings import generate_embedding

async def ingest_document(
        session: AsyncSession,
        filename: str,
        content: str,
        content_type: str | None = None,
        ) -> Document:
    document = Document(
        filename=filename,
        content_type=content_type,
    )
    session.add(document)
    await session.flush()

    chunks = chunk_text(content)
    for chunk in chunks:
        embedding = await generate_embedding(chunk)
        document_chunk = DocumentChunk(
            document_id=document.id,
            content=chunk,
            embedding=embedding,
        )
        session.add(document_chunk)
    await session.commit()
    await session.refresh(document)

    
    return document