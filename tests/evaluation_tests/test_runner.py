from evaluation.runner import build_report, evaluate_answers


def test_evaluation_report():
    actual_answers = {
        "q1": "Python is a programming language.",
        "q2": "RAG combines retrieval with generation to answer using external context.",
        "q3": "An AI agent can reason, use tools, and perform tasks.",
    }

    results = evaluate_answers(actual_answers)
    report = build_report(results)

    assert report["total_questions"] == 3
    assert report["passed"] == 3
    assert report["failed"] == 0
    assert report["accuracy"] == 1.0
    