from pydantic import BaseModel, Field
from app.agents.agent import Agent
from app.agents.state import AgentState
from app.agents.tool_provider import ToolProvider
from app.security.output_guard import validate_output
from app.llm.structured import StructuredLLMClient

class VerificationResult(BaseModel):
    supported: bool
    contradictions: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    citation_valid: bool
    verified_answer: str = ""
    reason: str

class VerificationAgent:
    def __init__(self, agent: Agent | None = None, tool_provider: ToolProvider | None = None, verifier=None) -> None:
        self.agent = agent or Agent()
        self.tool_provider = tool_provider
        self.verifier = verifier or StructuredLLMClient()

    async def run(self, query: str, context=None, event_callback=None, **kwargs) -> AgentState:
        tools = await self.tool_provider.get_tools() if self.tool_provider else []
        if context is None:
            self.agent.event_callback = event_callback
            return await self.agent.run(query=query, tools=tools, **kwargs)

        evidence = context.get("context", "") if isinstance(context, dict) else str(context)
        citations = context.get("citations", []) if isinstance(context, dict) else []
        proposed = context.get("final_answer", "") if isinstance(context, dict) else getattr(context, "final_answer", "")
        prompt = f"""Verify and, if supported, produce a grounded answer.\nQuestion: {query}\nEvidence: {evidence}\nProposed answer: {proposed}\nCitations: {citations}\nDo not invent facts. Mark unsupported claims. citation_valid must be true only when citations support the answer."""
        result = await self.verifier.generate(prompt=prompt, response_schema=VerificationResult)
        if not result.supported or not result.citation_valid:
            return AgentState(query=query, error=result.reason)
        answer = result.verified_answer.strip() or proposed.strip() or evidence.strip()
        try:
            answer = validate_output(answer)
        except ValueError as exc:
            return AgentState(query=query, error=str(exc))
        return AgentState(query=query, final_answer=answer)
