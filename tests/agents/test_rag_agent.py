import pytest

from app.agents.rag_agent import RAGAgent


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
            "context": "retrieved context",
            "citations": [],
            "chunks": [],
        }


@pytest.mark.asyncio
async def test_rag_agent():
    agent = RAGAgent(pipeline=MockPipeline())

    result = await agent.run(
        session=None,
        query="What is AegisAI?",
    )

    assert result["query"] == "What is AegisAI?"
    assert result["context"] == "retrieved context"