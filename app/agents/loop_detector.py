class LoopDetector:
    def __init__(self, max_repeats: int = 2) -> None:
        if max_repeats <= 0:
            raise ValueError("max_repeats must be greater than zero")
        self.max_repeats = max_repeats
        self._seen = {}

    def is_loop(self, task: str) -> bool:
        count = self._seen.get(task, 0) + 1
        self._seen[task] = count
        return count > self.max_repeats

    def reset(self) -> None:
        self._seen.clear()
