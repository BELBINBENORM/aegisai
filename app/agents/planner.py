from dataclasses import dataclass, field

from pydantic import BaseModel

from app.llm.structured import StructuredLLMClient


class PlannedTask(BaseModel):
    description: str


class PlannedTasks(BaseModel):
    tasks: list[PlannedTask]


@dataclass
class TaskPlan:
    query: str
    tasks: list[str] = field(default_factory=list)


class Planner:
    def __init__(
        self,
        client: StructuredLLMClient | None = None,
    ) -> None:
        self.client = client or StructuredLLMClient()

    async def plan(self, query: str) -> TaskPlan:
        prompt = f"""
Break the following user request into clear, independent tasks.

User request:
{query}

Return the minimum number of tasks needed to complete the request.
"""

        result = await self.client.generate(
            prompt=prompt,
            response_schema=PlannedTasks,
        )

        return TaskPlan(
            query=query,
            tasks=[
                task.description
                for task in result.tasks
            ],
        )