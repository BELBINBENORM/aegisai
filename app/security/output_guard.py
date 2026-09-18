def validate_output(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Invalid empty output')
    return text.strip()
