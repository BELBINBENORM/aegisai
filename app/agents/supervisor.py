from app.agents.multi_agent_state import MultiAgentState


class Supervisor:
    def __init__(self, agents: dict) -> None:
        self.agents = agents

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

        agent_name = self.route(query)
        state.set_current_agent(agent_name)

        agent = self.agents.get(agent_name)

        if agent is None:
            state.error = f"Unknown agent: {agent_name}"
            return state

        result = await agent.run(query=query, **kwargs)

        state.add_result(agent_name, result)

        return state