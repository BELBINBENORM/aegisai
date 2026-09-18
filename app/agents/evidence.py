import re
CITATION_PATTERN = re.compile(r"\[[0-9]+\]")

def verify_evidence(answer: str, citations=None) -> bool:
    if not answer or not answer.strip(): return False
    if citations is not None and citations:
        return True
    return bool(CITATION_PATTERN.search(answer))
