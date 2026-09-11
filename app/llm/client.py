import asyncio

from google import genai
from google.genai import errors

from app.config.settings import settings
from app.observability.latency import elapsed_time, start_timer
from app.observability.tokens import calculate_cost


class BaseLLMClient:
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
    ) -> str:
        raise NotImplementedError


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
        start = start_timer()

        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                latency = elapsed_time(start)

                usage = getattr(response, "usage_metadata", None)

                input_tokens = getattr(
                    usage,
                    "prompt_token_count",
                    0,
                ) or 0

                output_tokens = getattr(
                    usage,
                    "candidates_token_count",
                    0,
                ) or 0

                cost = calculate_cost(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )

                print(
                    f"LLM metrics: "
                    f"model={model} "
                    f"input_tokens={input_tokens} "
                    f"output_tokens={output_tokens} "
                    f"cost={cost:.6f} "
                    f"latency={latency:.3f}s"
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
        start = start_timer()

        response = await self.client.aio.models.generate_content_stream(
            model=model,
            contents=prompt,
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

        latency = elapsed_time(start)

        print(
            f"LLM stream metrics: "
            f"model={model} "
            f"latency={latency:.3f}s"
        )