def context_relevance(context: str, question: str) -> float:
    if not context.strip() or not question.strip():
        return 0.0

    question_words = set(question.lower().split())
    context_words = set(context.lower().split())

    overlap = question_words & context_words

    return len(overlap) / len(question_words)


def answer_relevance(answer: str, expected: str) -> float:
    if not answer.strip() or not expected.strip():
        return 0.0

    answer_words = set(answer.lower().split())
    expected_words = set(expected.lower().split())

    overlap = answer_words & expected_words

    return len(overlap) / len(expected_words)