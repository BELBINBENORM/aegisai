def routing_accuracy(
    expected_routes: list[str],
    actual_routes: list[str],
) -> float:
    if not expected_routes:
        return 0.0

    correct = sum(
        expected == actual
        for expected, actual in zip(expected_routes, actual_routes)
    )

    return correct / len(expected_routes)