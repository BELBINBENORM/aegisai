from app.agents.state import AgentState
from app.agents.tool import Tool
from app.agents.tool_runner import ToolRunner
from app.memory.manager import MemoryManager
from app.observability.tracing import log_agent, log_tool


class Agent:
    def __init__(
        self,
        tool_runner: ToolRunner | None = None,
        max_steps: int = 5,
        memory_manager: MemoryManager | None = None,
    ) -> None:
        self.tool_runner = tool_runner or ToolRunner()
        self.max_steps = max_steps
        self.memory_manager = memory_manager

    async def run(
        self,
        query: str,
        tools: list[Tool],
        user_id: str | None = None,
        request_id: str = "unknown",
    ) -> AgentState:
        state = AgentState(
            query=query,
            max_steps=self.max_steps,
        )

        log_agent(self.__class__.__name__, request_id)

        state.add_message("user", query)

        try:
            if self.memory_manager and user_id:
                memories = await self.memory_manager.search(
                    user_id=user_id,
                    query=query,
                )

                for memory in memories:
                    state.memory_context.add(memory)

                    state.add_message(
                        "memory",
                        memory.content,
                    )

            while state.can_continue():
                state.increment_step()

                response = await self.tool_runner.generate_response(
                    contents=state.messages,
                    tools=tools,
                )

                if response.function_calls:
                    function_call = response.function_calls[0]

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

                    arguments = function_call.args or {}

                    log_tool(tool.name, request_id)

                    result = await tool.execute(**arguments)

                    state.add_tool_call(
                        name=tool.name,
                        arguments=arguments,
                    )

                    state.add_message(
                        "tool",
                        str(result),
                    )

                    continue

                if response.text:
                    state.final_answer = response.text
                    break

            if state.final_answer is None and state.error is None:
                state.error = "Agent reached the maximum step limit."

        except Exception as exc:
            state.error = str(exc)

        return state