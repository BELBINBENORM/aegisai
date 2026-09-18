import time


def start_timer() -> float:
    return time.perf_counter()


def elapsed_time(start: float) -> float:
    return time.perf_counter() - start