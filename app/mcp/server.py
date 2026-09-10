from typing import Any

from app.mcp.resource import MCPResource
from app.mcp.prompt import MCPPrompt


class MCPServer:
    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}
        self._resources: dict[str, MCPResource] = {}
        self._prompts: dict[str, MCPPrompt] = {}

    def register_tool(self, tool: Any) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            tool.function_declaration
            for tool in self._tools.values()
        ]

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        tool = self._tools.get(name)

        if tool is None:
            raise ValueError(f"Unknown tool: {name}")

        return await tool.execute(**arguments)

    def register_resource(self, resource: MCPResource) -> None:
        self._resources[resource.uri] = resource


    def list_resources(self) -> list[dict[str, Any]]:
        return [
            resource.to_dict()
            for resource in self._resources.values()
        ]


    def read_resource(self, uri: str) -> Any:
        resource = self._resources.get(uri)

        if resource is None:
            raise ValueError(f"Unknown resource: {uri}")

        return resource.content

    def register_prompt(self, prompt: MCPPrompt) -> None:
        self._prompts[prompt.name] = prompt


    def list_prompts(self) -> list[dict[str, Any]]:
        return [
            prompt.to_dict()
            for prompt in self._prompts.values()
        ]


    def get_prompt(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> str:
        prompt = self._prompts.get(name)

        if prompt is None:
            raise ValueError(f"Unknown prompt: {name}")

        return prompt.render(**(arguments or {}))