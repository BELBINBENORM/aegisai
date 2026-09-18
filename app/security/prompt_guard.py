import re
from fastapi import HTTPException

INJECTION_PATTERNS = [
    r'ignore\s+(?:(?:all|any)\s+)?(?:previous\s+)?instructions',
    r'disregard\s+(?:(?:all|any)\s+)?(?:previous\s+)?instructions',
    r'reveal\s+(?:the\s+)?(?:system|developer)\s+prompt',
    r'disable\s+(?:your\s+)?security',
]

def check_prompt(text: str):
    if len(text) > 20000:
        raise HTTPException(413, 'Prompt too large')
    lowered = text.lower()
    if any(re.search(pattern, lowered) for pattern in INJECTION_PATTERNS):
        raise HTTPException(400, 'Prompt rejected by security policy')
