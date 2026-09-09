import pytest

from app.agents.gemini_router import GeminiAgentRouter


class MockResult:
    agent = "rag"


class MockClient:
    async def generate(self, prompt, response_schema):
        assert "rag" in prompt
        assert "research" in prompt
        assert "tool" in prompt
        assert "verification" in prompt
        return MockResult()


@pytest.mark.asyncio
async def test_gemini_router():
    router = GeminiAgentRouter(client=MockClient())

    result = await router.route(
        "What does my document say?"
    )

    assert result == "rag"