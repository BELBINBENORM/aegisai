from evaluation.retrieval_metrics import (
    retrieval_precision,
    retrieval_recall,
)


def test_retrieval_precision():
    retrieved = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc3"]

    assert retrieval_precision(retrieved, relevant) == 2 / 3


def test_retrieval_recall():
    retrieved = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc3"]

    assert retrieval_recall(retrieved, relevant) == 1.0


def test_empty_retrieved():
    assert retrieval_precision([], ["doc1"]) == 0.0
    assert retrieval_recall([], ["doc1"]) == 0.0


