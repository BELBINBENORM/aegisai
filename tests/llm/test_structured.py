import pytest
from pydantic import BaseModel

from app.llm.structured import StructuredLLMClient


class Answer(BaseModel):
    answer: str
    confidence: float


@pytest.mark.asyncio
async def test_structured_generation():
    client = StructuredLLMClient()

    result = await client.generate(
        prompt="Return a short answer saying that AegisAI is an AI system.",
        response_schema=Answer,
    )

    assert isinstance(result, Answer)
    assert result.answer
    assert 0 <= result.confidence <= 1