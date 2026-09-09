from app.agents.multi_agent_state import MultiAgentState
from app.agents.parallel import ParallelAgentExecutor
from app.agents.router import AgentRouter
from app.agents.planner import Planner
from app.agents.evaluator import AgentEvaluator
from app.agents.reflector import AgentReflector
from app.agents.loop_detector import LoopDetector
from app.agents.execution_limiter import ExecutionLimiter


class Supervisor:
    def __init__(
        self,
        agents: dict,
        parallel_executor: ParallelAgentExecutor | None = None,
        router: AgentRouter | None = None,
        planner: Planner | None = None,
        evaluator: AgentEvaluator | None = None,
        reflector: AgentReflector | None = None,
        max_reflections: int = 2,
        loop_detector: LoopDetector | None = None,
        execution_limiter: ExecutionLimiter | None = None,
    ) -> None:
        self.agents = agents
        self.parallel_executor = (
            parallel_executor or ParallelAgentExecutor()
        )
        self.router = router
        self.planner = planner
        self.evaluator = evaluator
        self.reflector = reflector
        self.max_reflections = max_reflections
        self.loop_detector = loop_detector or LoopDetector()
        self.execution_limiter = execution_limiter or ExecutionLimiter()

    def route(self, query: str) -> str:
        query_lower = query.lower()

        if any(word in query_lower for word in ["research", "web", "latest"]):
            return "research"

        if any(word in query_lower for word in ["search", "document", "rag"]):
            return "rag"

        if any(word in query_lower for word in ["calculate", "tool", "execute"]):
            return "tool"

        if any(word in query_lower for word in ["verify", "check", "validate"]):
            return "verification"

        return "research"

    async def run(
        self,
        query: str,
        **kwargs,
    ) -> MultiAgentState:
        state = MultiAgentState(query=query)

        try:
            if self.planner:
                plan = await self.planner.plan(query)

                if not plan.tasks:
                    state.error = "Planner returned no tasks."
                    return state

                for task in plan.tasks:
                    agent_name = (
                        await self.router.route(task)
                        if self.router
                        else self.route(task)
                    )

                    success = await self._execute_with_reflection(
                        task=task,
                        agent_name=agent_name,
                        state=state,
                        **kwargs,
                    )

                    if not success:
                        return state

            else:
                agent_name = (
                    await self.router.route(query)
                    if self.router
                    else self.route(query)
                )

                success = await self._execute_with_reflection(
                    task=query,
                    agent_name=agent_name,
                    state=state,
                    **kwargs,
                )

                if not success:
                    return state

        except Exception as exc:
            state.error = str(exc)

        return state

    def handoff(
        self,
        state: MultiAgentState,
        from_agent: str,
        to_agent: str,
        context=None,
    ) -> MultiAgentState:
        state.set_current_agent(to_agent)

        if context is not None:
            existing_results = state.agent_results.get(from_agent, [])

            if context not in existing_results:
                state.add_result(
                    from_agent,
                    context,
                )

        return state

    async def run_parallel(
        self,
        queries: dict[str, str],
        **kwargs,
    ) -> MultiAgentState:
        state = MultiAgentState(
            query="; ".join(queries.values())
        )

        tasks = []

        for agent_name, query in queries.items():
            agent = self.agents.get(agent_name)

            if agent is None:
                state.error = f"Unknown agent: {agent_name}"
                continue

            state.set_current_agent(agent_name)
            tasks.append(
                agent.run(
                    query=query,
                    **kwargs,
                )
            )

        results = await self.parallel_executor.run(tasks)

        for agent_name, result in zip(queries.keys(), results):
            if isinstance(result, Exception):
                state.error = str(result)
                continue

            state.add_result(
                agent_name,
                result,
            )

        return state

    async def run_handoff(
        self,
        query: str,
        from_agent: str,
        to_agent: str,
        **kwargs,
    ) -> MultiAgentState:
        state = MultiAgentState(query=query)

        source_agent = self.agents.get(from_agent)
        target_agent = self.agents.get(to_agent)

        if source_agent is None:
            state.error = f"Unknown agent: {from_agent}"
            return state

        if target_agent is None:
            state.error = f"Unknown agent: {to_agent}"
            return state

        try:
            source_result = await source_agent.run(
                query=query,
                **kwargs,
            )

            state.add_result(
                from_agent,
                source_result,
            )

            state.set_current_agent(to_agent)

            target_result = await target_agent.run(
                query=query,
                context=source_result,
                **kwargs,
            )

            state.add_result(
                to_agent,
                target_result,
            )

        except Exception as exc:
            state.error = str(exc)

        return state


    async def _execute_with_reflection(
        self,
        task: str,
        agent_name: str,
        state: MultiAgentState,
        **kwargs,
    ) -> bool:
        agent = self.agents.get(agent_name)

        if agent is None:
            state.error = f"Unknown agent: {agent_name}"
            return False

        current_task = task

        for attempt in range(self.max_reflections + 1):

            if not self.execution_limiter.allow():
                state.error = "Execution limit exceeded."
                return False
    
            if self.loop_detector.is_loop(current_task):
                state.error = f"Loop detected for task: {current_task}"
                return False

            state.set_current_agent(agent_name)

            result = await agent.run(
                query=current_task,
                **kwargs,
            )

            state.add_result(
                agent_name,
                result,
            )

            if not self.evaluator:
                return True

            evaluation = await self.evaluator.evaluate(
                query=current_task,
                result=result,
            )

            if evaluation.sufficient:
                return True

            if (
                self.reflector is None
                or attempt >= self.max_reflections
            ):
                state.error = evaluation.reason
                return False

            reflection = await self.reflector.reflect(
                query=current_task,
                result=result,
                reason=evaluation.reason,
            )

            if not reflection.revised_task.strip():
                state.error = "Reflector returned an empty revised task."
                return False

            current_task = reflection.revised_task

        return False