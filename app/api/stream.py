import asyncio, json, uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.api.auth import get_current_user_id
from app.api.sessions import owned
from app.database.connection import get_db
from app.schemas.api import ChatRequest
from app.agents.main_agent import MainAgent
from app.llm.client import LLMClient

router = APIRouter(tags=['streaming'])
client = LLMClient()

@router.get('/stream')
async def legacy_stream(prompt: str):
    async def generate():
        async for token in client.generate_stream(prompt):
            yield f'data: {token}\n\n'
        yield 'data: [DONE]\n\n'
    return StreamingResponse(generate(), media_type='text/event-stream')

@router.post('/sessions/{sid}/chat/stream')
async def stream(sid: int, req: ChatRequest, request: Request, user_id=Depends(get_current_user_id), db=Depends(get_db)):
    await owned(db, user_id, sid)
    q = asyncio.Queue()
    rid = getattr(request.state, 'request_id', str(uuid.uuid4()))
    async def emit(event, data): await q.put({'event': event, 'data': data})
    async def work():
        try:
            result = await MainAgent().run(db, user_id, sid, req.message, rid, emit)
            await q.put({'event': 'final', 'data': result})
        except Exception as exc:
            await q.put({'event': 'error', 'data': str(exc)})
    task = asyncio.create_task(work())
    async def gen():
        while not task.done() or not q.empty():
            try:
                item = await asyncio.wait_for(q.get(), 0.2)
                yield f'data: {json.dumps(item, default=str)}\n\n'
            except asyncio.TimeoutError:
                continue
        yield 'data: [DONE]\n\n'
    return StreamingResponse(gen(), media_type='text/event-stream')
