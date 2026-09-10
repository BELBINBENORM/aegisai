from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.agents.state import AgentState
from app.main import app


client = TestClient(app)


def test_agent_stream():
    state = AgentState(
        query="hello",
        max_steps=5,
    )
    state.final_answer = "Hello from agent"

    with patch(
        "app.api.agent_stream.agent.run",
        new=AsyncMock(return_value=state),
    ):
        response = client.get(
            "/agent/stream",
            params={"prompt": "hello"},
        )

    assert response.status_code == 200
    assert '"event": "agent_started"' in response.text
    assert '"event": "response"' in response.text
    assert "Hello from agent" in response.text
    assert '"event": "agent_completed"' in response.text
    assert "data: [DONE]" in response.text