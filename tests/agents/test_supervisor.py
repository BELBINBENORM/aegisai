import pytest

from app.agents.supervisor import Supervisor


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