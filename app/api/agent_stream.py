import asyncio, json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.supervisor import Supervisor
from app.agents.rag_agent import RAGAgent
from app.agents.research_agent import ResearchAgent
from app.agents.tool_agent import ToolAgent
from app.agents.verification_agent import VerificationAgent
from app.api.auth import verify_api_key
from app.api.rate_limit import rate_limit
from app.database.connection import get_db

router = APIRouter(prefix='/agent', tags=['agent'], dependencies=[Depends(verify_api_key), Depends(rate_limit)])

def build_supervisor():
    return Supervisor(agents={'rag': RAGAgent(), 'research': ResearchAgent(), 'tool': ToolAgent(), 'verification': VerificationAgent()}, verify_final=True)

@router.get('/stream')
async def agent_stream(request: Request, prompt: str, session: AsyncSession = Depends(get_db)):
    async def generate():
        queue = asyncio.Queue()
        supervisor = build_supervisor()
        async def emit(event, data): await queue.put({'event': event, 'data': data})
        for agent in supervisor.agents.values():
            inner = getattr(agent, 'agent', None)
            if inner is not None: inner.event_callback = emit
        task = asyncio.create_task(supervisor.run(query=prompt, session=session, request_id=getattr(request.state, 'request_id', ''), event_callback=emit))
        await queue.put({'event': 'agent_started'})
        while not task.done() or not queue.empty():
            try:
                event = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield f'data: {json.dumps(event, default=str)}\n\n'
            except asyncio.TimeoutError:
                continue
        state = await task
        if state.error:
            yield f'data: {json.dumps({"event":"error","data":state.error})}\n\n'
        yield f'data: {json.dumps({"event":"agent_completed"})}\n\n'
        yield 'data: [DONE]\n\n'
    return StreamingResponse(generate(), media_type='text/event-stream')
