from app.llm.client import LLMClient


class MemorySummarizer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def summarize(self, memories: list[str]) -> str:
        if not memories:
            return ""

        prompt = (
            "Summarize these user memories into a short, useful profile. "
            "Keep only stable preferences, facts, and useful context.\n\n"
            + "\n".join(f"- {memory}" for memory in memories)
        )

        response = await self.llm.generate(prompt)

        return response.strip()