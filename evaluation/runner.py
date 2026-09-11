import asyncio
import json
from pathlib import Path

from evaluation.metrics import answer_matches
from evaluation.judge import judge_answer


BASE_DIR = Path(__file__).parent


def load_json(filename: str):
    with open(BASE_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def build_evaluation_dataset():
    questions = load_json("questions.json")
    expected_answers = load_json("expected_answers.json")

    expected = {
        item["id"]: item["expected"]
        for item in expected_answers
    }

    return [
        {
            "id": item["id"],
            "question": item["question"],
            "expected": expected.get(item["id"]),
        }
        for item in questions
    ]


def evaluate_answers(actual_answers: dict[str, str]):
    results = []

    for item in build_evaluation_dataset():
        actual = actual_answers.get(item["id"], "")

        judge = asyncio.run(
            judge_answer(
                actual,
                item["expected"],
            )
        )

        results.append({
            "id": item["id"],
            "question": item["question"],
            "expected": item["expected"],
            "actual": actual,
            "passed": answer_matches(
                item["expected"],
                actual,
            ),
            "judge_score": judge["score"],
            "judge_reason": judge["reason"],
        })

    return results


def build_report(results):
    total = len(results)
    passed = sum(
        result["passed"]
        for result in results
    )

    judge_scores = [
        result["judge_score"]
        for result in results
    ]

    average_judge_score = (
        sum(judge_scores) / len(judge_scores)
        if judge_scores
        else 0.0
    )

    return {
        "total_questions": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": passed / total if total else 0.0,
        "average_judge_score": average_judge_score,
    }


if __name__ == "__main__":
    actual_answers = {
        "q1": "Python is a programming language.",
        "q2": "RAG combines retrieval with generation to answer using external context.",
        "q3": "An AI agent can reason, use tools, and perform tasks.",
    }

    results = evaluate_answers(actual_answers)

    with open(
        BASE_DIR / "evaluation_results.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    report = build_report(results)

    with open(
        BASE_DIR / "evaluation_report.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    for result in results:
        print(result)

    print("\nEvaluation Report:")
    print(report)