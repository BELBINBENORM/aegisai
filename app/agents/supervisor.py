from app.agents.multi_agent_state import MultiAgentState
from app.agents.parallel import ParallelAgentExecutor
from app.agents.router import AgentRouter
from app.agents.planner import Planner
from app.agents.evaluator import AgentEvaluator
from app.agents.reflector import AgentReflector
from app.agents.loop_detector import LoopDetector
from app.agents.execution_limiter import ExecutionLimiter
import inspect


class Supervisor:
    def __init__(self, agents: dict, parallel_executor=None, router=None,
                 planner=None, evaluator=None, reflector=None, max_reflections=2,
                 loop_detector=None, execution_limiter=None, verify_final=False) -> None:
        self.agents = agents
        self.parallel_executor = parallel_executor or ParallelAgentExecutor()
        self.router = router
        self.planner = planner
        self.evaluator = evaluator
        self.reflector = reflector
        self.max_reflections = max_reflections
        self.verify_final = verify_final
        self._loop_detector_factory = lambda: LoopDetector(
            max_repeats=(loop_detector.max_repeats if loop_detector else 2)
        )
        self._execution_limiter_factory = lambda: ExecutionLimiter(
            max_attempts=(execution_limiter.max_attempts if execution_limiter else 5)
        )

    def route(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["research", "web", "latest"]): return "research"
        if any(w in q for w in ["search", "document", "rag"]): return "rag"
        if any(w in q for w in ["calculate", "tool", "execute"]): return "tool"
        if any(w in q for w in ["verify", "check", "validate"]): return "verification"
        return "research"

    async def run(self, query: str, **kwargs) -> MultiAgentState:
        state = MultiAgentState(query=query)
        limiter = self._execution_limiter_factory()
        loop_detector = self._loop_detector_factory()
        try:
            tasks = [query]
            if self.planner:
                plan = await self.planner.plan(query)
                tasks = plan.tasks
                if not tasks:
                    state.error = "Planner returned no tasks."
                    return state
            for task in tasks:
                agent_name = await self.router.route(task) if self.router else self.route(task)
                if not await self._execute_with_reflection(task, agent_name, state, limiter, loop_detector, **kwargs):
                    return state
            if self.verify_final and "verification" in self.agents and state.current_agent != "verification" and state.agent_results:
                source = state.current_agent
                source_result = state.agent_results[source][-1]
                state.set_current_agent("verification")
                verified = await self._call_agent(self.agents["verification"], query, context=source_result, **kwargs)
                state.add_result("verification", verified)
        except Exception as exc:
            state.error = str(exc)
        return state

    def handoff(self, state, from_agent, to_agent, context=None):
        state.set_current_agent(to_agent)
        if context is not None:
            existing = state.agent_results.get(from_agent, [])
            if context not in existing:
                state.add_result(from_agent, context)
        return state

    async def run_parallel(self, queries: dict[str, str], **kwargs) -> MultiAgentState:
        state = MultiAgentState(query="; ".join(queries.values()))
        tasks = []
        names = []
        for name, query in queries.items():
            agent = self.agents.get(name)
            if agent is None:
                state.error = f"Unknown agent: {name}"
                continue
            names.append(name)
            tasks.append(self._call_agent(agent, query, **kwargs))
        results = await self.parallel_executor.run(tasks)
        for name, result in zip(names, results):
            if isinstance(result, Exception): state.error = str(result)
            else: state.add_result(name, result)
        return state

    async def run_handoff(self, query, from_agent, to_agent, **kwargs):
        state = MultiAgentState(query=query)
        source = self.agents.get(from_agent); target = self.agents.get(to_agent)
        if source is None: state.error = f"Unknown agent: {from_agent}"; return state
        if target is None: state.error = f"Unknown agent: {to_agent}"; return state
        try:
            source_result = await self._call_agent(source, query, **kwargs)
            state.add_result(from_agent, source_result)
            state.set_current_agent(to_agent)
            target_result = await self._call_agent(target, query, context=source_result, **kwargs)
            state.add_result(to_agent, target_result)
        except Exception as exc: state.error = str(exc)
        return state

    async def _execute_with_reflection(self, task, agent_name, state, limiter, loop_detector, **kwargs):
        agent = self.agents.get(agent_name)
        if agent is None:
            state.error = f"Unknown agent: {agent_name}"; return False
        current_task = task
        for attempt in range(self.max_reflections + 1):
            if not limiter.allow():
                state.error = "Execution limit exceeded."
                return False

            if loop_detector.is_loop(current_task):
                state.error = f"Loop detected for task: {current_task}"
                return False

            state.set_current_agent(agent_name)
            result = await self._call_agent(agent, current_task, **kwargs)
            state.add_result(agent_name, result)

            if not self.evaluator:
                return True

            evaluation = await self.evaluator.evaluate(
                query=current_task,
                result=result,
            )

            if evaluation.sufficient:
                return True

            # The final allowed attempt must stop without creating
            # another reflection. max_reflections counts reflections,
            # so max_reflections=2 permits 3 agent attempts.
            if attempt >= self.max_reflections:
                state.error = evaluation.reason
                return False

            if not self.reflector:
                state.error = evaluation.reason
                return False

            reflection = await self.reflector.reflect(
                current_task,
                result,
                evaluation.reason,
            )
            current_task = reflection.revised_task

        state.error = "Maximum reflection attempts exceeded."
        return False

    async def _call_agent(self, agent, query: str, **kwargs):
        sig = inspect.signature(agent.run)
        accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        if accepts_kwargs:
            return await agent.run(query=query, **kwargs)
        allowed = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return await agent.run(query=query, **allowed)
