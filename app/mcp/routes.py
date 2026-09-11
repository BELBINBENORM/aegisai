from typing import Any
from pydantic import Field
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.mcp.server import MCPServer
from app.agents.tool import Tool

from app.mcp.auth import authorize_tool, require_api_key


class EchoTool(Tool):
    name = "echo"
    description = "Echo text"
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
        },
        "required": ["text"],
    }

    async def execute(self, **kwargs):
        return kwargs["text"]


router = APIRouter(prefix="/mcp")

server = MCPServer()
server.register_tool(EchoTool())

class ToolCallRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


@router.get("/tools", dependencies=[Depends(require_api_key)])
async def list_tools():
    return {"tools": server.list_tools()}


@router.post("/tools/{name}")
async def call_tool(
    name: str,
    request: ToolCallRequest,
    allowed_tools: set[str] = Depends(require_api_key),
):
    authorize_tool(allowed_tools, name)

    try:
        result = await server.call_tool(name, request.arguments)
        return {"result": result}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/resources", dependencies=[Depends(require_api_key)])
async def list_resources():
    return {"resources": server.list_resources()}


@router.get("/resources/{uri:path}", dependencies=[Depends(require_api_key)])
async def read_resource(uri: str):
    try:
        return {"content": server.read_resource(uri)}
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

@router.get("/prompts", dependencies=[Depends(require_api_key)])
async def list_prompts():
    return {"prompts": server.list_prompts()}


@router.post("/prompts/{name}", dependencies=[Depends(require_api_key)])
async def get_prompt(
    name: str,
    request: ToolCallRequest,
):
    try:
        result = server.get_prompt(
            name,
            request.arguments,
        )
        return {"prompt": result}
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
