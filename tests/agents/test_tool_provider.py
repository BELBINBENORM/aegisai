import pytest

from app.agents.local_tool_provider import LocalToolProvider


@pytest.mark.asyncio
async def test_local_tool_provider():
    provider = LocalToolProvider(tools=[])

    tools = await provider.get_tools()

    assert tools == []