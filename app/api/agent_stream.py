import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agents.agent import Agent

router = APIRouter(prefix="/agent", tags=["agent"])

agent = Agent()


@router.get("/stream")
async def agent_stream(prompt: str):
    async def generate():
        yield f"data: {json.dumps({'event': 'agent_started'})}\n\n"

        state = await agent.run(
            query=prompt,
            tools=[],
        )

        if state.final_answer:
            yield f"data: {json.dumps({'event': 'response', 'data': state.final_answer})}\n\n"

        if state.error:
            yield f"data: {json.dumps({'event': 'error', 'data': state.error})}\n\n"

        yield f"data: {json.dumps({'event': 'agent_completed'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )