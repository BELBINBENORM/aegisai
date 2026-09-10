import asyncio
from abc import ABC, abstractmethod


from google import genai
from google.genai import errors

from app.config.settings import settings


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str | None = None) -> str:
        pass


class LLMClient(BaseLLMClient):
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )

    async def generate(
        self,
        prompt: str,
        model: str = "gemini-3.6-flash",
        max_retries: int = 3,
    ) -> str:
        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text

            except errors.ServerError:
                if attempt == max_retries - 1:
                    raise

                await asyncio.sleep(2 ** attempt)

        raise RuntimeError("LLM generation failed")

    async def generate_stream(
        self,
        prompt: str,
        model: str = "gemini-3.6-flash",
    ):
        response = await self.client.aio.models.generate_content_stream(
            model=model,
            contents=prompt,
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text