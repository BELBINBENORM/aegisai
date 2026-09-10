import logging


logger = logging.getLogger("aegisai")


def log_request(request_id: str, method: str, path: str) -> None:
    logger.info(
        "request_id=%s method=%s path=%s",
        request_id,
        method,
        path,
    )