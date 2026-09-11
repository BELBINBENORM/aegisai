from typing import Any

from app.agents.approval import ApprovalManager
from app.agents.tool import Tool
from app.llm.function_calling import FunctionCallingClient
from app.observability.tracing import log_tool


class ToolRunner:
    def __init__(
        self,
        function_calling_client: FunctionCallingClient | None = None,
        approval_manager: ApprovalManager | None = None,
    ) -> None:
        self.client = function_calling_client or FunctionCallingClient()
        self.approval_manager = approval_manager or ApprovalManager()

    async def run(
        self,
        prompt: str,
        tools: list[Tool],
        request_id: str = "unknown",
    ) -> Any:
        declarations = self._get_declarations(tools)

        function_call = await self.client.generate_function_call(
            prompt=prompt,
            function_declarations=declarations,
        )

        if function_call is None:
            return None

        for tool in tools:
            if tool.name == function_call.name:
                arguments = function_call.args or {}

                approval = self.approval_manager.request(
                    f"execute tool: {tool.name}"
                )

                if not self.approval_manager.can_execute(approval):
                    return {
                        "tool_name": tool.name,
                        "arguments": arguments,
                        "status": "approval_required",
                        "approval": approval,
                    }

                log_tool(tool.name, request_id)

                return {
                    "tool_name": tool.name,
                    "arguments": arguments,
                    "result": await tool.execute(**arguments),
                }

        raise ValueError(
            f"Unknown tool requested: {function_call.name}"
        )

    async def generate_response(
        self,
        contents: list[Any],
        tools: list[Tool],
    ) -> Any:
        declarations = self._get_declarations(tools)
        return await self.client.generate_response(
            contents=contents,
            function_declarations=declarations,
        )

    def _get_declarations(self, tools: list[Tool]) -> list:
        return [tool.function_declaration for tool in tools]