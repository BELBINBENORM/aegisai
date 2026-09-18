import re
from app.security.prompt_guard import INJECTION_PATTERNS

def check_retrieved_content(text: str) -> None:
    normalized = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, normalized):
            raise ValueError('Potential indirect prompt injection detected')
