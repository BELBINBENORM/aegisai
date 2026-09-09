class MockPipeline:
    async def retrieve(
        self,
        session,
        query,
        top_k=5,
        metadata_filter=None,
    ):
        return {
            "query": query,
            "rewritten_query": query,
            "context": "retrieved context",
            "citations": [],
            "chunks": [],
        }