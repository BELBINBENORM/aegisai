from dataclasses import dataclass


@dataclass
class RetrievalMetrics:
    precision: float
    recall: float


def evaluate_retrieval(
    retrieved_ids: list[int],
    relevant_ids: set[int],
) -> RetrievalMetrics:
    if not retrieved_ids:
        return RetrievalMetrics(precision=0.0, recall=0.0)

    retrieved_set = set(retrieved_ids)
    relevant_retrieved = retrieved_set & relevant_ids

    precision = len(relevant_retrieved) / len(retrieved_set)

    recall = (
        len(relevant_retrieved) / len(relevant_ids)
        if relevant_ids
        else 0.0
    )

    return RetrievalMetrics(
        precision=precision,
        recall=recall,
    )