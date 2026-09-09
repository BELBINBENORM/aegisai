from app.agents.execution_limiter import ExecutionLimiter


def test_execution_limiter_allows_attempts():
    limiter = ExecutionLimiter(max_attempts=2)

    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is False


def test_execution_limiter_reset():
    limiter = ExecutionLimiter(max_attempts=1)

    assert limiter.allow() is True
    assert limiter.allow() is False

    limiter.reset()

    assert limiter.allow() is True