from typing import Any


class MCPResource:
    def __init__(
        self,
        uri: str,
        name: str,
        content: Any,
    ) -> None:
        self.uri = uri
        self.name = name
        self.content = content

    def to_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "content": self.content,
        }