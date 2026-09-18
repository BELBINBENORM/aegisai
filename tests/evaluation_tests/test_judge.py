import pytest

from evaluation.judge import judge_answer


@pytest.mark.asyncio
async def test_matching_answer():
    result = await judge_answer(
        "Python is a programming language.",
        "Python is a programming language.",
    )

    assert result["score"] == 1


@pytest.mark.asyncio
async def test_wrong_answer():
    result = await judge_answer(
        "Python is a database.",
        "Python is a programming language.",
    )

    assert result["score"] == 0


@pytest.mark.asyncio
async def test_empty_answer():
    result = await judge_answer(
        "",
        "Python is a programming language.",
    )

    assert result["score"] == 0