from app.agents.verification import verify_answer


def test_verification_accepts_valid_answer():
    assert verify_answer(
        "Python is a programming language [1]."
    ) is True


def test_verification_rejects_empty_answer():
    assert verify_answer("") is False


def test_verification_rejects_answer_without_evidence():
    assert verify_answer(
        "Python is a programming language."
    ) is False