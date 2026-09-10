from typing import Any


class MCPPrompt:
    def __init__(
        self,
        name: str,
        template: str,
    ) -> None:
        self.name = name
        self.template = template

    def render(self, **kwargs: Any) -> str:
        return self.template.format(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "template": self.template,
        }