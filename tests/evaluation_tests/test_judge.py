from evaluation.judge import judge_answer


def test_matching_answer():
    result = judge_answer(
        "Python is a programming language.",
        "Python is a programming language.",
    )

    assert result["score"] == 1


def test_wrong_answer():
    result = judge_answer(
        "Python is a database.",
        "Python is a programming language.",
    )

    assert result["score"] == 0


def test_empty_answer():
    result = judge_answer(
        "",
        "Python is a programming language.",
    )

    assert result["score"] == 0