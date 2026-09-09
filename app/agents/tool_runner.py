from typing import Any

from app.agents.tool import Tool
from app.llm.function_calling import FunctionCallingClient


class ToolRunner:
    def __init__(
        self,
        function_calling_client: FunctionCallingClient | None = None,
    ) -> None:
        self.client = function_calling_client or FunctionCallingClient()

    async def run(
        self,
        prompt: str,
        tools: list[Tool],
    ) -> Any:
        declarations = [
            tool.function_declaration
            for tool in tools
        ]

        function_call = await self.client.generate_function_call(
            prompt=prompt,
            function_declarations=declarations,
        )

        if function_call is None:
            return None

        for tool in tools:
            if tool.name == function_call.name:
                arguments = function_call.args or {}
                return await tool.execute(**arguments)

        raise ValueError(
            f"Unknown tool requested: {function_call.name}"
        )