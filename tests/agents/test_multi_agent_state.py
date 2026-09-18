from app.agents.multi_agent_state import MultiAgentState


def test_multi_agent_state():
    state = MultiAgentState(query="test")

    assert state.query == "test"
    assert state.current_agent is None
    assert state.completed_agents == []

    state.set_current_agent("rag")
    state.add_result("rag", {"context": "hello"})

    assert state.current_agent == "rag"
    assert state.agent_results["rag"] == [
        {"context": "hello"}
    ]
    assert state.completed_agents == ["rag"]


def test_multi_agent_state_does_not_duplicate_agents():
    state = MultiAgentState(query="test")

    state.add_result("rag", "first")
    state.add_result("rag", "second")

    assert state.completed_agents == ["rag"]
    assert state.agent_results["rag"] == [
        "first",
        "second",
    ]


def test_multi_agent_state_preserves_multiple_results_for_same_agent():
    state = MultiAgentState(
        query="multiple tasks",
    )

    state.add_result("research", "result 1")
    state.add_result("research", "result 2")

    assert state.agent_results["research"] == [
        "result 1",
        "result 2",
    ]

    assert state.completed_agents == ["research"]