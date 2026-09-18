from app.agents.evidence import verify_evidence


def test_accepts_answer_with_citation():
    answer = "Python is a programming language [1]."

    assert verify_evidence(answer) is True


def test_rejects_answer_without_citation():
    answer = "Python is a programming language."

    assert verify_evidence(answer) is False


def test_rejects_empty_answer():
    assert verify_evidence("") is False
    