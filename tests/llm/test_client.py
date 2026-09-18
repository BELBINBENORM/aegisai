from unittest.mock import AsyncMock, patch

from google.genai import errors
import pytest

from app.llm.client import BaseLLMClient, LLMClient


def test_llm_client_implements_base():
    client = LLMClient()
    assert isinstance(client, BaseLLMClient)



@pytest.mark.asyncio
async def test_llm_retries_on_server_error():
    client = LLMClient()

    mock_response = type("Response", (), {"text": "success"})()

    with patch.object(
        client.client.aio.models,
        "generate_content",
        new_callable=AsyncMock,
        side_effect=[
            errors.ServerError("temporary failure", response_json={}),
            mock_response,
        ],
    ) as mock_generate:
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await client.generate("test", max_retries=2)

    assert result == "success"
    assert mock_generate.call_count == 2