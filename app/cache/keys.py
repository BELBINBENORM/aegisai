import hashlib, json
def response_key(user_id: int, session_id: int, query: str, model: str, version: str = "v1") -> str:
    raw = json.dumps([user_id, session_id, query.strip(), model, version], separators=(",", ":"), ensure_ascii=False)
    return "aegisai:cache:response:" + hashlib.sha256(raw.encode()).hexdigest()
def retrieval_key(session_id: int, query: str, config: str = "v1") -> str:
    raw = f"{session_id}:{config}:{query.strip()}"; return "aegisai:cache:retrieval:" + hashlib.sha256(raw.encode()).hexdigest()


def build_response_cache_key(query: str, user_id: str | int, session_id: str | int | None = None, model: str = "gemini-3.6-flash", version: str = "v1") -> str:
    return response_key(user_id, session_id or "global", query, model, version)
