import hashlib


def build_response_cache_key(
    query: str,
    user_id: str | None = None,
) -> str:
    value = f"{user_id or 'anonymous'}:{query}"

    query_hash = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    return f"response:{query_hash}"