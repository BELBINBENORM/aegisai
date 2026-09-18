from typing import Any, Literal
from pydantic import BaseModel, Field

class SessionCreate(BaseModel): name: str = Field(min_length=1, max_length=255); metadata: dict[str, Any] = Field(default_factory=dict)
class SessionUpdate(BaseModel): name: str | None = Field(default=None, min_length=1, max_length=255); metadata: dict[str, Any] | None = None
class SessionOut(BaseModel): id: int; name: str; status: str = "active"
class ChatRequest(BaseModel): message: str = Field(min_length=1, max_length=20000)
class CitationOut(BaseModel): document_id: int; chunk_id: int; filename: str; page: int | None = None
class ClarificationOption(BaseModel): id: str; label: str; recommended: bool = False
class Clarification(BaseModel): type: Literal["clarification"]; message: str; options: list[ClarificationOption] = []; allow_custom: bool = True
class ChatResponse(BaseModel): status: Literal["completed", "clarification", "error"]; answer: str | None = None; clarification: Clarification | None = None; citations: list[CitationOut] = []; request_id: str
class DocumentOut(BaseModel): id: int; filename: str; status: str; job_id: str | None = None
