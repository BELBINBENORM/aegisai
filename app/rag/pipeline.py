from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.citations import build_citations
from app.rag.compression import compress_context
from app.rag.multi_query import MultiQueryGenerator
from app.rag.query_rewriter import QueryRewriter
from app.rag.reranker import rerank_chunks
from app.rag.hybrid_search import hybrid_search
from app.observability.retrieval import log_retrieval


class RAGPipeline:
    def __init__(
        self,
        query_rewriter: QueryRewriter | None = None,
        multi_query_generator: MultiQueryGenerator | None = None,
    ) -> None:
        self.query_rewriter = query_rewriter or QueryRewriter()
        self.multi_query_generator = (
            multi_query_generator or MultiQueryGenerator()
        )

    async def retrieve(
        self,
        session: AsyncSession,
        query: str,
        top_k: int = 5,
        metadata_filter: dict | None = None,
        request_id: str = "unknown",
    ):
        rewritten_query = await self.query_rewriter.rewrite(query)

        queries = await self.multi_query_generator.generate(
            rewritten_query,
            count=3,
        )

        if rewritten_query not in queries:
            queries.insert(0, rewritten_query)

        all_chunks = []
        seen_ids = set()

        for search_query in queries:
            chunks = await hybrid_search(
                session=session,
                query=search_query,
                top_k=top_k,
                metadata_filter=metadata_filter,
            )

            for chunk in chunks:
                if chunk.id not in seen_ids:
                    all_chunks.append(chunk)
                    seen_ids.add(chunk.id)

        ranked_chunks = rerank_chunks(
            query=rewritten_query,
            chunks=all_chunks,
            top_k=top_k,
        )

        log_retrieval(
            request_id=request_id,
            query=query,
            result_count=len(ranked_chunks),
        )
        
        context = compress_context(ranked_chunks)

        citations = build_citations(ranked_chunks)

        return {
            "query": query,
            "rewritten_query": rewritten_query,
            "context": context,
            "citations": citations,
            "chunks": ranked_chunks,
        }