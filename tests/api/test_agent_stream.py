from unittest.mock import AsyncMock, patch
from app.config.settings import settings
from fastapi.testclient import TestClient
from app.agents.multi_agent_state import MultiAgentState
from app.main import app
client = TestClient(app)

def test_agent_stream():
    state = MultiAgentState(query="hello")
    state.set_current_agent("research")
    state.add_result("research", "Hello from supervisor")
    with patch("app.api.agent_stream.Supervisor.run", new=AsyncMock(return_value=state)):
        response = client.get("/agent/stream", params={"prompt":"hello"}, headers={"X-API-Key":settings.api_key})
    assert response.status_code == 200
    assert '"event": "agent_started"' in response.text
    assert '"event": "agent_completed"' in response.text
    assert "data: [DONE]" in response.text

def test_agent_stream_requires_api_key():
    assert client.get("/agent/stream", params={"prompt":"hello"}).status_code == 401
