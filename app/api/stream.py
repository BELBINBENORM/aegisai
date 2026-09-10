from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.llm.client import LLMClient

router = APIRouter(prefix="/stream", tags=["stream"])

client = LLMClient()


@router.get("")
async def stream_response(prompt: str):
    async def generate():
        async for chunk in client.generate_stream(prompt):
            yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )