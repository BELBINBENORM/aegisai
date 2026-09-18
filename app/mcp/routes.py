from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from app.mcp.auth import require_mcp_key
from app.mcp.server import server
from app.mcp.tools.rag import hybrid_search
from app.mcp.tools.memory import get_chat_history, get_memories
from app.mcp.tools.web import search_web
from app.database.connection import get_db

router = APIRouter(prefix='/mcp', tags=['mcp'])
class ToolCall(BaseModel): arguments: dict[str, Any] = Field(default_factory=dict)

def init_tools():
    if server.tools: return
    server.register('hybrid_search','Hybrid vector and keyword document retrieval',{'type':'object','required':['session_id','query']},hybrid_search)
    server.register('get_chat_history','Get recent session conversation',{'type':'object','required':['session_id']},get_chat_history)
    server.register('get_memories','Get session memories',{'type':'object','required':['user_id','session_id']},get_memories)
    server.register('search_web','Search configured external web provider',{'type':'object','required':['query']},search_web)
init_tools()

@router.get('/tools', dependencies=[Depends(require_mcp_key)])
async def tools(request: Request):
    # X-API-Key is retained as a legacy MCP transport alias. New clients use X-MCP-API-Key.
    if request.headers.get('X-API-Key') and not request.headers.get('X-MCP-API-Key'):
        return {'tools': [{'name':'echo','description':'Echo text','inputSchema':{'type':'object','properties':{'text':{'type':'string'}}}}]}
    return {'tools': server.list_tools()}

@router.post('/tools/{name}', dependencies=[Depends(require_mcp_key)])
async def call(name: str, req: ToolCall, request: Request, db=Depends(get_db)):
    legacy = bool(request.headers.get('X-API-Key') and not request.headers.get('X-MCP-API-Key'))
    if legacy:
        if name != 'echo': raise HTTPException(403, 'Tool is not allowed')
        return {'result': req.arguments.get('text','')}
    args = dict(req.arguments); args['db'] = db
    if name not in server.tools: raise HTTPException(403, 'Tool is not allowed')
    try: return {'result': await server.call(name, args)}
    except Exception as e: raise HTTPException(400, str(e))

@router.get('/resources', dependencies=[Depends(require_mcp_key)])
async def resources(): return {'resources': server.list_resources()}
@router.get('/prompts', dependencies=[Depends(require_mcp_key)])
async def prompts(): return {'prompts': server.list_prompts()}
