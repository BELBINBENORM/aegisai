from app.agents.loop_detector import LoopDetector


def test_loop_detector_allows_repeated_tasks():
    detector = LoopDetector(max_repeats=2)

    assert detector.is_loop("research AI") is False
    assert detector.is_loop("research AI") is False


def test_loop_detector_detects_loop():
    detector = LoopDetector(max_repeats=2)

    detector.is_loop("research AI")
    detector.is_loop("research AI")

    assert detector.is_loop("research AI") is True


def test_loop_detector_tracks_tasks_independently():
    detector = LoopDetector(max_repeats=2)

    assert detector.is_loop("task A") is False
    assert detector.is_loop("task B") is False
    assert detector.is_loop("task A") is False
    assert detector.is_loop("task B") is False


def test_loop_detector_reset():
    detector = LoopDetector(max_repeats=2)

    detector.is_loop("research AI")
    detector.is_loop("research AI")
    detector.reset()

    assert detector.is_loop("research AI") is False