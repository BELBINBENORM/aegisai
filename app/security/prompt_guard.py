import re


INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all instructions",
    r"disregard previous instructions",
    r"system prompt",
    r"reveal your instructions",
    r"reveal the system prompt",
]


def check_prompt(text: str) -> None:
    normalized = text.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, normalized):
            raise ValueError("Potential prompt injection detected")