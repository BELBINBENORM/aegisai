import logging
from app.security.pii import redact_pii
logger = logging.getLogger("aegisai")
def log_retrieval(request_id: str, query: str, result_count: int) -> None:
    logger.info("request_id=%s trace=%s retrieval_query=%s query=%s result_count=%s", request_id, request_id, redact_pii(query), redact_pii(query), result_count)
