from abc import ABC, abstractmethod
from typing import AsyncIterator
import asyncio
from app.config.settings import settings

class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system: str = '', max_retries: int = 3) -> str: ...
    @abstractmethod
    def stream(self, prompt: str, system: str = '') -> AsyncIterator[str]: ...

class LLMClient(BaseLLMClient):
    def __init__(self):
        self.client = None
        if settings.gemini_api_key:
            from google import genai
            self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate(self, prompt: str, system: str = '', max_retries: int = 3) -> str:
        if not self.client:
            return 'LLM is not configured. Configure GEMINI_API_KEY to generate an answer.'
        config = {'system_instruction': system} if system else None
        attempts = max(1, max_retries)
        for attempt in range(attempts):
            try:
                response = await self.client.aio.models.generate_content(
                    model=settings.model_name, contents=prompt, config=config
                )
                return response.text or ''
            except Exception as exc:
                # Retry transient Gemini server failures, but surface other errors immediately.
                try:
                    from google.genai import errors
                    retryable = isinstance(exc, errors.ServerError)
                except Exception:
                    retryable = False
                if not retryable or attempt >= attempts - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError('LLM generation failed')

    async def stream(self, prompt: str, system: str = '') -> AsyncIterator[str]:
        if not self.client:
            yield 'LLM is not configured. Configure GEMINI_API_KEY to generate an answer.'
            return
        config = {'system_instruction': system} if system else None
        stream = self.client.aio.models.generate_content_stream(
            model=settings.model_name, contents=prompt, config=config
        )
        if hasattr(stream, '__await__'):
            stream = await stream
        async for chunk in stream:
            if getattr(chunk, 'text', None):
                yield chunk.text

    async def generate_stream(self, prompt: str, system: str = '') -> AsyncIterator[str]:
        async for token in self.stream(prompt, system):
            yield token
