def validate_output(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Invalid empty output")

    return text.strip()