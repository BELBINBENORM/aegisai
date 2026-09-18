from typing import Any, Awaitable, Callable
from app.mcp.resource import MCPResource
from app.mcp.prompt import MCPPrompt

class MCPServer:
    def __init__(self):
        self.tools: dict[str, dict[str, Any]] = {}
        self.resources: dict[str, MCPResource] = {}
        self.prompts: dict[str, MCPPrompt] = {}

    def register(self, name, description, schema, handler: Callable[..., Awaitable[Any]]):
        self.tools[name] = {'name': name, 'description': description, 'inputSchema': schema, 'handler': handler}

    def register_tool(self, tool):
        async def handler(**kwargs): return await tool.execute(**kwargs)
        self.register(tool.name, tool.description, getattr(tool, 'parameters', {'type': 'object'}), handler)

    def list_tools(self):
        return [{k: v for k, v in t.items() if k != 'handler'} for t in self.tools.values()]

    async def call(self, name, arguments):
        if name not in self.tools: raise ValueError(f'Unknown tool: {name}')
        return await self.tools[name]['handler'](**arguments)

    async def call_tool(self, name, arguments): return await self.call(name, arguments)

    def register_resource(self, resource: MCPResource): self.resources[resource.uri] = resource
    def list_resources(self): return [r.to_dict() for r in self.resources.values()]
    def read_resource(self, uri):
        if uri not in self.resources: raise ValueError(f'Unknown resource: {uri}')
        return self.resources[uri].content

    def register_prompt(self, prompt: MCPPrompt): self.prompts[prompt.name] = prompt
    def list_prompts(self): return [p.to_dict() for p in self.prompts.values()]
    def get_prompt(self, name, arguments):
        if name not in self.prompts: raise ValueError(f'Unknown prompt: {name}')
        return self.prompts[name].render(**arguments)

server = MCPServer()
