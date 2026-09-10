import re


CITATION_PATTERN = re.compile(
    r"\[[0-9]+\]"
)


def verify_evidence(answer: str) -> bool:
    if not answer.strip():
        return False

    return bool(CITATION_PATTERN.search(answer))