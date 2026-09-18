from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.pipeline import RAGPipeline


class RAGAgent:
    def __init__(
        self,
        pipeline: RAGPipeline | None = None,
    ) -> None:
        self.pipeline = pipeline or RAGPipeline()

    async def run(
        self,
        session: AsyncSession,
        query: str,
        top_k: int = 5,
        metadata_filter: dict | None = None,
        request_id: str = "unknown",
    ) -> dict:
        result = await self.pipeline.retrieve(
            session=session,
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter,
            request_id=request_id,
        )

        return {
            "query": result["query"],
            "rewritten_query": result["rewritten_query"],
            "context": result["context"],
            "citations": result["citations"],
            "chunks": result["chunks"],
        }