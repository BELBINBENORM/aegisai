from typing import Any

from app.agents.approval import ApprovalManager
from app.agents.tool import Tool

approval_manager_global = ApprovalManager()
pending_tool_calls: dict[str, tuple[Tool, dict[str, Any], str]] = {}
from app.llm.function_calling import FunctionCallingClient
from app.observability.tracing import log_tool


class ToolRunner:
    def __init__(
        self,
        function_calling_client: FunctionCallingClient | None = None,
        approval_manager: ApprovalManager | None = None,
    ) -> None:
        self.client = function_calling_client or FunctionCallingClient()
        self.approval_manager = approval_manager or approval_manager_global

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
            approval_manager = approval_manager_global
            self.approval_manager = approval_manager

        approval = approval_manager.request(
            f"execute sensitive tool: {tool.name}"
        )
        pending_tool_calls[approval.id] = (tool, arguments, request_id)

        # Persist approval state when Redis is available.
        import asyncio
        try:
            asyncio.create_task(approval_manager.persist(approval))
        except RuntimeError:
            pass

        if not approval_manager.can_execute(approval):
            return {
                "tool_name": tool.name,
                "arguments": arguments,
                "status": "approval_required",
                "approval": approval.__dict__,
            }

        log_tool(tool.name, request_id)

        result = await tool.execute(**arguments)

        return {
            "tool_name": tool.name,
            "arguments": arguments,
            "result": result,
            "status": "completed",
        }

    async def resume_approved(self, approval_id: str) -> dict[str, Any]:
        approval = await self.approval_manager.get(approval_id)
        if approval is None:
            raise ValueError("Approval not found")
        if not self.approval_manager.can_execute(approval):
            raise ValueError("Approval has not been granted")
        pending = pending_tool_calls.pop(approval_id, None)
        if pending is None:
            raise ValueError("Pending tool execution is no longer available")
        tool, arguments, request_id = pending
        result = await tool.execute(**arguments)
        return {"tool_name": tool.name, "arguments": arguments, "result": result, "status": "completed"}

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