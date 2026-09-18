import pytest
from pydantic import BaseModel

from app.llm.structured import StructuredLLMClient


class Answer(BaseModel):
    answer: str
    confidence: float


class MockResponse:
    text = '{"answer": "AegisAI is an AI system.", "confidence": 0.95}'


@pytest.mark.asyncio
async def test_structured_generation(monkeypatch):
    client = StructuredLLMClient()

    async def mock_generate_content(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        client.client.aio.models,
        "generate_content",
        mock_generate_content,
    )

    result = await client.generate(
        prompt="Return a short answer saying that AegisAI is an AI system.",
        response_schema=Answer,
    )

    assert isinstance(result, Answer)
    assert result.answer == "AegisAI is an AI system."
    assert 0 <= result.confidence <= 1