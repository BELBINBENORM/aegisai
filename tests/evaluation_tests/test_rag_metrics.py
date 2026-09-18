from evaluation.rag_metrics import (
    answer_relevance,
    context_relevance,
)


def test_context_relevance():
    context = "Python is a programming language used for software development."
    question = "What is Python?"

    score = context_relevance(context, question)

    assert score > 0


def test_answer_relevance():
    answer = "Python is a programming language."
    expected = "Python is a programming language."

    assert answer_relevance(answer, expected) == 1.0


def test_empty_context():
    assert context_relevance("", "What is Python?") == 0.0


def test_empty_answer():
    assert answer_relevance("", "Python is a language.") == 0.0