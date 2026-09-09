from typing import TypeVar

from pydantic import BaseModel
from google import genai

from app.config.settings import settings


T = TypeVar("T", bound=BaseModel)


class StructuredLLMClient:
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )

    async def generate(
        self,
        prompt: str,
        response_schema: type[T],
        model: str = "gemini-3.6-flash",
    ) -> T:
        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            },
        )

        return response_schema.model_validate_json(response.text)