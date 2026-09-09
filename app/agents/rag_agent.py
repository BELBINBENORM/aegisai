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
    ):
        return await self.pipeline.retrieve(
            session=session,
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )