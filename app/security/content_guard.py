from app.security.prompt_guard import INJECTION_PATTERNS


def check_retrieved_content(text: str) -> None:
    normalized = text.lower()

    for pattern in INJECTION_PATTERNS:
        if pattern in normalized:
            raise ValueError(
                "Potential indirect prompt injection detected"
            )