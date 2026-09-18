import logging

logger = logging.getLogger("aegisai")


def log_error(request_id: str, error: Exception) -> None:
    logger.error(
        "request_id=%s error=%s",
        request_id,
        error,
    )