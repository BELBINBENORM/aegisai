from app.agents.state import AgentState
from app.agents.tool import Tool
from app.agents.tool_runner import ToolRunner
from app.memory.manager import MemoryManager
from app.observability.tracing import log_agent

from app.cache.cache import get_cached, set_cached
from app.cache.keys import build_response_cache_key

from app.security.prompt_guard import check_prompt
from app.security.output_guard import validate_output
import inspect


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
        self.event_callback = None

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

        check_prompt(query)

        log_agent(self.__class__.__name__, request_id)

        state.add_message("user", query)
        cache_key = None

        if user_id and not self.memory_manager and not tools:
            cache_key = build_response_cache_key(
                query=query,
                user_id=user_id,
            )

            cached_answer = await get_cached(cache_key)

            if cached_answer:
                state.final_answer = cached_answer
                return state

        try:
            # Load semantic memory
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

            # Agent loop
            while state.can_continue():
                state.increment_step()

                if not tools:
                    streamed = []
                    stream = self.tool_runner.client.client.aio.models.generate_content_stream(
                        model="gemini-3.6-flash",
                        contents=state.messages,
                    )
                    if inspect.isawaitable(stream):
                        stream = await stream
                    async for token in stream:
                        if token.text:
                            streamed.append(token.text)
                            if self.event_callback:
                                await self.event_callback("token", {"text": token.text})
                    response_text = "".join(streamed)
                    state.final_answer = validate_output(response_text)

                    if cache_key:
                        await set_cached(
                            cache_key,
                            response_text,
                            expire=300,
                        )

                    break

                response = await self.tool_runner.generate_response(
                    contents=state.messages,
                    tools=tools,
                )

                # Tool call requested by LLM
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

                    if self.event_callback:
                        await self.event_callback(
                            "tool_started",
                            {
                                "tool": tool.name,
                            },
                        )

                    # Execute through ToolRunner so HITL approval
                    # cannot be bypassed.
                    tool_result = await self.tool_runner.run_tool(
                        tool=tool,
                        arguments=arguments,
                        request_id=request_id,
                    )

                    # Human approval required
                    if tool_result.get("status") == "approval_required":
                        state.error = "Tool execution requires approval."

                        state.add_tool_call(
                            name=tool.name,
                            arguments=arguments,
                        )

                        state.add_message(
                            "tool",
                            str(tool_result),
                        )

                        if self.event_callback:
                            await self.event_callback(
                                "approval_required",
                                {
                                    "tool": tool.name,
                                    "arguments": arguments,
                                    "approval": tool_result.get(
                                        "approval"
                                    ),
                                },
                            )

                        break

                    # Tool execution completed
                    result = tool_result["result"]

                    if self.event_callback:
                        await self.event_callback(
                            "tool_completed",
                            {
                                "tool": tool.name,
                            },
                        )

                    state.add_tool_call(
                        name=tool.name,
                        arguments=arguments,
                    )

                    state.add_message(
                        "tool",
                        str(result),
                    )

                    continue

                # Final LLM response
                if response.text:
                    state.final_answer = validate_output(
                        response.text
                    )

                    if cache_key:
                        await set_cached(
                            cache_key,
                            response.text,
                            expire=300,
                        )

                    break

            if state.final_answer is None and state.error is None:
                state.error = (
                    "Agent reached the maximum step limit."
                )

        except Exception as exc:
            state.error = str(exc)

        return state