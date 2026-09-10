from datetime import datetime
from app.agents.state import AgentState
from app.memory.context import MemoryContext
from app.memory.models import Memory

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

def test_agent_state_has_memory_context(): 
    state = AgentState(query="What is Python?") 

    assert isinstance(state.memory_context, MemoryContext) 
    assert state.memory_context.memories == [] 

def test_agent_state_can_add_memory(): 
    state = AgentState(query="What is Python?") 
    state.memory_context.add( 
        Memory(
            id="memory-1", 
            user_id="user-1", 
            content="User likes Python.", 
            metadata={}, 
            created_at=datetime.now(), 
        ) 
    ) 
    assert state.memory_context.contents() == ["User likes Python."] 