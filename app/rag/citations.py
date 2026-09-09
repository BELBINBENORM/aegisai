from dataclasses import dataclass

from app.database.models import DocumentChunk


@dataclass
class Citation:
    document_id: int
    chunk_id: int
    filename: str
    content: str


def build_citations(
    chunks: list[DocumentChunk],
) -> list[Citation]:
    citations = []

    for chunk in chunks:
        document = chunk.document

        citations.append(
            Citation(
                document_id=chunk.document_id,
                chunk_id=chunk.id,
                filename=document.filename,
                content=chunk.content,
            )
        )

    return citations