from typing import Any

from google import genai
from google.genai import types

from app.config.settings import settings
from app.llm.retry import with_retries


class FunctionCallingClient:
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )

    async def generate_function_call(
        self,
        prompt: str,
        function_declarations: list[dict[str, Any]],
        model: str = "gemini-3.6-flash",
    ):
        tool = types.Tool(
            function_declarations=function_declarations
        )

        config = types.GenerateContentConfig(
            tools=[tool],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )

        async def operation():
            return await self.client.aio.models.generate_content(model=model, contents=prompt, config=config)
        response = await with_retries(operation)

        function_calls = response.function_calls

        if not function_calls:
            return None

        return function_calls[0]

    async def generate_response(
        self,
        contents: list[Any],
        function_declarations: list[dict[str, Any]],
        model: str = "gemini-3.6-flash",
    ):
        tool = types.Tool(
            function_declarations=function_declarations
        )

        config = types.GenerateContentConfig(
            tools=[tool],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )

        async def operation():
            return await self.client.aio.models.generate_content(model=model, contents=contents, config=config)
        return await with_retries(operation)