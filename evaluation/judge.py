from app.llm.client import LLMClient


async def judge_answer(
    answer: str,
    expected: str,
    llm_client: LLMClient | None = None,
) -> dict:
    if not answer.strip():
        return {
            "score": 0,
            "reason": "Answer is empty",
        }

    if answer.strip().lower() == expected.strip().lower():
        return {
            "score": 1,
            "reason": "Answer matches expected answer",
        }

    client = llm_client or LLMClient()

    prompt = f"""
Evaluate the following answer against the expected answer.

Expected answer:
{expected}

Actual answer:
{answer}

Return only one of these formats:

SCORE: 1
REASON: <short explanation>

or

SCORE: 0
REASON: <short explanation>
"""

    response = await client.generate(prompt)

    lines = response.strip().splitlines()

    score = 0
    reason = response.strip()

    for line in lines:
        if line.startswith("SCORE:"):
            try:
                score = int(line.split(":", 1)[1].strip())
                score = 1 if score == 1 else 0
            except ValueError:
                score = 0

        elif line.startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()

    return {
        "score": score,
        "reason": reason,
    }