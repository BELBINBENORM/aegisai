import pytest

from app.agents.planner import Planner


class MockStructuredLLMClient:
    async def generate(self, prompt, response_schema):
        return response_schema(
            tasks=[
                {"description": "Research AegisAI architecture"},
                {"description": "Verify the research findings"},
            ]
        )


@pytest.mark.asyncio
async def test_planner_decomposes_query():
    planner = Planner(
        client=MockStructuredLLMClient(),
    )

    plan = await planner.plan(
        "Research and verify AegisAI architecture"
    )

    assert plan.query == "Research and verify AegisAI architecture"
    assert plan.tasks == [
        "Research AegisAI architecture",
        "Verify the research findings",
    ]