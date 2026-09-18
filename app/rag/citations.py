def build_citations(chunks):
    return [
        {
            "document_id": chunk.document_id,
            "chunk_id": chunk.id,
            "filename": chunk.document.filename if getattr(chunk, "document", None) else None,
            "page": getattr(chunk, "page", None),
        }
        for chunk in chunks
    ]


def citations(chunks):
    return build_citations(chunks)
