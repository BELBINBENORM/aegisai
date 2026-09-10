from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Memory:
    id: str
    user_id: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime