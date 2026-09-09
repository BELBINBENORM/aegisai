from typing import Any

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
        tools:list[Tool],
    ) -> AgentState:
        state = AgentState(
            query=query,
            max_steps=self.max_steps,
        )

        state.add_message("user", query)

        try:
            while state.can_continue():
                state.increment_step()

                result = await self.tool_runner.run(
                    prompt=query,
                    tools=tools,
                )

                if result is not None:
                    state.final_answer = str(result)
                    break

            if state.final_answer is None and state.error is None:
                state.error = "Agent reached the maximum step limit."

        except Exception as exc:
            state.error = str(exc)

        return state 