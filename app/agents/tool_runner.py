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

    async def run_tool(
        self,
        tool: Tool,
        arguments: dict[str, Any],
        request_id: str = "unknown",
    ) -> dict[str, Any]:
        """
        Execute a tool.

        Normal tools execute immediately.
        Sensitive tools require explicit human approval.
        """

        # Normal tools do not require HITL.
        if not tool.requires_approval:
            log_tool(tool.name, request_id)

            result = await tool.execute(**arguments)

            return {
                "tool_name": tool.name,
                "arguments": arguments,
                "result": result,
                "status": "completed",
            }

        # Be compatible with test/custom ToolRunner subclasses
        # that don't call ToolRunner.__init__().
        approval_manager = getattr(
            self,
            "approval_manager",
            None,
        )

        if approval_manager is None:
            approval_manager = ApprovalManager()
            self.approval_manager = approval_manager

        approval = approval_manager.request(
            f"execute sensitive tool: {tool.name}"
        )

        if not approval_manager.can_execute(approval):
            return {
                "tool_name": tool.name,
                "arguments": arguments,
                "status": "approval_required",
                "approval": approval,
            }

        log_tool(tool.name, request_id)

        result = await tool.execute(**arguments)

        return {
            "tool_name": tool.name,
            "arguments": arguments,
            "result": result,
            "status": "completed",
        }

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

        tool = next(
            (
                tool
                for tool in tools
                if tool.name == function_call.name
            ),
            None,
        )

        if tool is None:
            raise ValueError(
                f"Unknown tool requested: {function_call.name}"
            )

        return await self.run_tool(
            tool=tool,
            arguments=function_call.args or {},
            request_id=request_id,
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

    def _get_declarations(
        self,
        tools: list[Tool],
    ) -> list[dict[str, Any]]:
        return [
            tool.function_declaration
            for tool in tools
        ]