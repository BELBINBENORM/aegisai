import hashlib
from pathlib import Path
from uuid import uuid4
from typing import Any
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Document, DocumentChunk, Session
from app.rag.chunking import chunk_text
from app.rag.embeddings import EmbeddingProvider
from app.rag.loaders.text import load_file

async def ingest_document(session: AsyncSession, document_id: int | None = None, storage_root: str | None = None, chunk_size=1200, overlap=150, *, filename: str | None = None, content: str | None = None, content_type: str = 'text/plain', document_metadata: dict[str, Any] | None = None):
    if document_id is None:
        if filename is None or content is None: raise ValueError('filename and content are required when document_id is omitted')
        raw = content.encode(); checksum = hashlib.sha256(raw).hexdigest()
        owner = (await session.execute(select(Session).where(Session.user_id == 1).order_by(Session.id))).scalar_one_or_none()
        if owner is None:
            owner = Session(user_id=1, name='Test ingestion'); session.add(owner); await session.flush()
        document = Document(session_id=owner.id, filename=filename, content_type=content_type, storage_key=f'inline-{uuid4().hex}-{checksum}', checksum=checksum, size_bytes=len(raw), status='processing', document_metadata=document_metadata or {})
        session.add(document); await session.commit(); await session.refresh(document)
        pages=[(None, content, None)]
    else:
        document=(await session.execute(select(Document).where(Document.id == document_id))).scalar_one()
        document.status='processing'; document.error=None; await session.commit()
        pages=load_file(str(Path(storage_root or './storage') / document.storage_key), Path(document.filename).suffix.lower())
    try:
        await session.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
        embedder=EmbeddingProvider(); index=0
        for page, text, section in pages:
            for chunk in chunk_text(text, chunk_size, overlap, page, section):
                vec=await embedder.embed(chunk.text)
                session.add(DocumentChunk(document_id=document.id, session_id=document.session_id, chunk_index=index, content=chunk.text, page=page, section=section, search_text=chunk.text, embedding=vec)); index += 1
        document.status='ready'; document.error=None; await session.commit(); await session.refresh(document)
        return document
    except Exception as exc:
        await session.rollback()
        fresh=(await session.execute(select(Document).where(Document.id == document.id))).scalar_one_or_none()
        if fresh:
            fresh.status='failed'; fresh.error=str(exc); await session.commit()
        raise
