import logging

logger = logging.getLogger("aegisai")


def log_agent(agent_name: str, request_id: str) -> None:
    logger.info(
        "request_id=%s agent=%s",
        request_id,
        agent_name,
    )


def log_tool(tool_name: str, request_id: str) -> None:
    logger.info(
        "request_id=%s tool=%s",
        request_id,
        tool_name,
    )