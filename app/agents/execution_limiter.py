class ExecutionLimiter:
    def __init__(self, max_attempts: int = 5) -> None:
        self.max_attempts = max_attempts
        self.attempts = 0

    def allow(self) -> bool:
        if self.attempts >= self.max_attempts:
            return False

        self.attempts += 1
        return True

    def reset(self) -> None:
        self.attempts = 0