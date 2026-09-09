from app.agents.state import AgentState


def test_agent_state():
    state = AgentState(query="What is AegisAI?")

    assert state.query == "What is AegisAI?"
    assert state.step_count == 0
    assert state.can_continue()

    state.add_message("user", "What is AegisAI?")
    state.add_tool_call("search", {"query": "AegisAI"})
    state.increment_step()

    assert len(state.messages) == 1
    assert len(state.tool_calls) == 1
    assert state.step_count == 1


def test_agent_step_limit():
    state = AgentState(
        query="test",
        max_steps=2,
    )

    assert state.can_continue()

    state.increment_step()
    assert state.can_continue()

    state.increment_step()
    assert not state.can_continue()