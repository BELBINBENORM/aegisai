from unittest.mock import AsyncMock

import pytest

from app.memory.summarizer import MemorySummarizer


@pytest.mark.asyncio
async def test_memory_summarizer():
    llm = AsyncMock()
    llm.generate.return_value = (
        "User prefers Python and concise answers."
    )

    summarizer = MemorySummarizer(llm)

    result = await summarizer.summarize(
        [
            "User likes Python.",
            "User prefers concise answers.",
            "User is building an AI application.",
        ]
    )

    assert result == "User prefers Python and concise answers."

    llm.generate.assert_awaited_once()

@pytest.mark.asyncio
async def test_memory_summarizer_empty():
    llm = AsyncMock()

    summarizer = MemorySummarizer(llm)

    result = await summarizer.summarize([])

    assert result == ""
    llm.generate.assert_not_awaited()