from app.agents.state import AgentState
from app.agents.tool import Tool
from app.agents.tool_runner import ToolRunner


class Agent:
    def __init__(
        self,
        tool_runner: ToolRunner | None = None,
        max_steps: int = 5,
    ) -> None:
        self.tool_runner = tool_runner or ToolRunner()
        self.max_steps = max_steps

    async def run(
        self,
        query: str,
        tools: list[Tool],
    ) -> AgentState:
        state = AgentState(
            query=query,
            max_steps=self.max_steps,
        )

        state.add_message("user", query)

        try:
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