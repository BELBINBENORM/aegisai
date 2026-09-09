import pytest

from app.agents.supervisor import Supervisor
from app.agents.multi_agent_state import MultiAgentState

class MockAgent:
    def __init__(self, result):
        self.result = result

    async def run(self, query, **kwargs):
        return self.result


def build_supervisor():
    return Supervisor(
        agents={
            "rag": MockAgent("rag result"),
            "research": MockAgent("research result"),
            "tool": MockAgent("tool result"),
            "verification": MockAgent("verification result"),
        }
    )


def test_supervisor_routes_rag():
    supervisor = build_supervisor()
    assert supervisor.route("search my documents") == "rag"


def test_supervisor_routes_research():
    supervisor = build_supervisor()
    assert supervisor.route("research the latest AI news") == "research"


def test_supervisor_routes_tool():
    supervisor = build_supervisor()
    assert supervisor.route("calculate this using a tool") == "tool"


def test_supervisor_routes_verification():
    supervisor = build_supervisor()
    assert supervisor.route("verify this answer") == "verification"


def test_supervisor_default_route():
    supervisor = build_supervisor()
    assert supervisor.route("tell me something") == "research"

def test_supervisor_handoff():
    supervisor = build_supervisor()

    state = MultiAgentState(query="verify this")

    state.set_current_agent("rag")
    state.add_result("rag", {"context": "retrieved evidence"})

    result = supervisor.handoff(
        state=state,
        from_agent="rag",
        to_agent="verification",
        context={"context": "retrieved evidence"},
    )

    assert result.current_agent == "verification"
    assert result.agent_results["rag"] == {
        "context": "retrieved evidence"
    }
    assert "rag" in result.completed_agents


@pytest.mark.asyncio
async def test_supervisor_runs_selected_agent():
    supervisor = build_supervisor()

    state = await supervisor.run(
        "search my documents",
    )

    assert state.current_agent == "rag"
    assert state.agent_results["rag"] == "rag result"
    assert state.completed_agents == ["rag"]
    assert state.error is None

@pytest.mark.asyncio
async def test_supervisor_handles_agent_failure():
    class FailingAgent:
        async def run(self, query, **kwargs):
            raise RuntimeError("agent failed")

    supervisor = Supervisor(
        agents={
            "research": FailingAgent(),
        }
    )

    state = await supervisor.run("research something")

    assert state.current_agent == "research"
    assert state.error == "agent failed"
    assert state.agent_results == {}

@pytest.mark.asyncio
async def test_supervisor_runs_agents_in_parallel():
    supervisor = build_supervisor()

    state = await supervisor.run_parallel(
        queries={
            "rag": "search documents",
            "research": "research latest AI",
        }
    )

    assert state.agent_results["rag"] == "rag result"
    assert state.agent_results["research"] == "research result"
    assert "rag" in state.completed_agents
    assert "research" in state.completed_agents
    assert state.error is None


@pytest.mark.asyncio
async def test_supervisor_parallel_preserves_success_on_failure():
    class FailingAgent:
        async def run(self, query, **kwargs):
            raise RuntimeError("research failed")

    supervisor = Supervisor(
        agents={
            "rag": MockAgent("rag result"),
            "research": FailingAgent(),
        }
    )

    state = await supervisor.run_parallel(
        queries={
            "rag": "search documents",
            "research": "research latest AI",
        }
    )

    assert state.agent_results["rag"] == "rag result"
    assert "research" not in state.agent_results
    assert state.error == "research failed"

@pytest.mark.asyncio
async def test_supervisor_runs_rag_to_verification_handoff():
    class MockRAGAgent:
        async def run(self, query, **kwargs):
            return {
                "context": "retrieved evidence",
                "citations": ["citation-1"],
            }

    class MockVerificationAgent:
        async def run(self, query, context=None, **kwargs):
            assert context == {
                "context": "retrieved evidence",
                "citations": ["citation-1"],
            }

            return "verified result"

    supervisor = Supervisor(
        agents={
            "rag": MockRAGAgent(),
            "verification": MockVerificationAgent(),
        }
    )

    state = await supervisor.run_handoff(
        query="What does the document say?",
        from_agent="rag",
        to_agent="verification",
    )

    assert state.current_agent == "verification"
    assert state.agent_results["rag"]["context"] == "retrieved evidence"
    assert state.agent_results["verification"] == "verified result"
    assert state.completed_agents == ["rag", "verification"]
    assert state.error is None

@pytest.mark.asyncio
async def test_supervisor_handoff_preserves_source_on_target_failure():
    class MockRAGAgent:
        async def run(self, query, **kwargs):
            return {"context": "evidence"}

    class FailingVerificationAgent:
        async def run(self, query, context=None, **kwargs):
            raise RuntimeError("verification failed")

    supervisor = Supervisor(
        agents={
            "rag": MockRAGAgent(),
            "verification": FailingVerificationAgent(),
        }
    )

    state = await supervisor.run_handoff(
        query="Verify this",
        from_agent="rag",
        to_agent="verification",
    )

    assert state.agent_results["rag"] == {"context": "evidence"}
    assert "verification" not in state.agent_results
    assert state.current_agent == "verification"
    assert state.error == "verification failed"


@pytest.mark.asyncio
async def test_supervisor_uses_custom_router():
    class MockRouter:
        async def route(self, query):
            return "rag"

    supervisor = Supervisor(
        agents={
            "rag": MockAgent("rag result"),
            "research": MockAgent("research result"),
        },
        router=MockRouter(),
    )

    state = await supervisor.run(
        "Tell me something",
    )

    assert state.current_agent == "rag"
    assert state.agent_results["rag"] == "rag result"
    assert state.error is None