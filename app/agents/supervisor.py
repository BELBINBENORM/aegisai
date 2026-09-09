from app.agents.multi_agent_state import MultiAgentState
from app.agents.parallel import ParallelAgentExecutor
from app.agents.router import AgentRouter

class Supervisor:
    def __init__(
        self,
        agents: dict,
        parallel_executor: ParallelAgentExecutor | None = None,
        router: AgentRouter | None = None,
    ) -> None:
        self.agents = agents
        self.parallel_executor = (
            parallel_executor or ParallelAgentExecutor()
        )
        self.router = router

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

        if self.router:
            agent_name = await self.router.route(query)
        else:
            agent_name = self.route(query)
            
        state.set_current_agent(agent_name)

        agent = self.agents.get(agent_name)

        if agent is None:
            state.error = f"Unknown agent: {agent_name}"
            return state

        try:
            result = await agent.run(query=query, **kwargs)
            state.add_result(agent_name, result)
        except Exception as exc:
            state.error = str(exc)

        return state

    def handoff(
        self,
        state: MultiAgentState,
        from_agent: str,
        to_agent: str,
        context,
    ) -> MultiAgentState:
        state.set_current_agent(to_agent)

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
            tasks.append(agent.run(query=query, **kwargs))

        results = await self.parallel_executor.run(tasks)

        for agent_name, result in zip(queries.keys(), results):
            if isinstance(result, Exception):
                state.error = str(result)
                continue

            state.add_result(agent_name, result)

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