from evaluation.routing_metrics import routing_accuracy


def test_routing_accuracy():
    expected = ["rag", "research", "tool"]
    actual = ["rag", "research", "tool"]

    assert routing_accuracy(expected, actual) == 1.0


def test_partial_routing_accuracy():
    expected = ["rag", "research", "tool"]
    actual = ["rag", "tool", "tool"]

    assert routing_accuracy(expected, actual) == 2 / 3


def test_empty_expected_routes():
    assert routing_accuracy([], []) == 0.0


def test_extra_actual_routes_are_ignored():
    expected = ["rag"]
    actual = ["rag", "tool"]

    assert routing_accuracy(expected, actual) == 1.0