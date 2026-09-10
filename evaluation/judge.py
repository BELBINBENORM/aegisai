def judge_answer(answer: str, expected: str) -> dict:
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

    return {
        "score": 0,
        "reason": "Answer does not match expected answer",
    }