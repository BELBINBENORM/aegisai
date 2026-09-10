def retrieval_precision(retrieved: list[str], relevant: list[str]) -> float:
    if not retrieved:
        return 0.0

    relevant_items = set(relevant)
    hits = sum(item in relevant_items for item in retrieved)

    return hits / len(retrieved)


def retrieval_recall(retrieved: list[str], relevant: list[str]) -> float:
    if not relevant:
        return 0.0

    relevant_items = set(relevant)
    hits = sum(item in relevant_items for item in retrieved)

    return hits / len(relevant_items)