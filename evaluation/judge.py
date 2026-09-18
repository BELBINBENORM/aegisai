async def judge_answer(answer: str, expected: str):
    if not answer or not expected: return {'score': 0}
    return {'score': int(answer.strip().casefold() == expected.strip().casefold())}

def judge_separate_from_exact_match(): return True
