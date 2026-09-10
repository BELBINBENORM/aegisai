import logging

logger = logging.getLogger("aegisai")


def log_retrieval(
    request_id: str,
    query: str,
    result_count: int,
) -> None:
    logger.info(
        "request_id=%s retrieval_query=%s result_count=%s",
        request_id,
        query,
        result_count,
    )