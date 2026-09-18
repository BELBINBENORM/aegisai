import logging
from contextvars import ContextVar
from contextlib import contextmanager
from app.security.pii import redact_pii

logger = logging.getLogger("aegisai")
_current_trace: ContextVar[str] = ContextVar("aegisai_trace", default="unknown")

def set_trace_id(request_id: str):
    return _current_trace.set(request_id)

def get_trace_id() -> str:
    return _current_trace.get()

@contextmanager
def trace_span(name: str):
    logger.info("trace=%s span_start=%s", get_trace_id(), redact_pii(name))
    try: yield
    finally: logger.info("trace=%s span_end=%s", get_trace_id(), redact_pii(name))

def log_agent(agent_name: str, request_id: str = "unknown") -> None:
    logger.info("request_id=%s trace=%s agent=%s", request_id or get_trace_id(), request_id or get_trace_id(), redact_pii(agent_name))

def log_tool(tool_name: str, request_id: str = "unknown") -> None:
    logger.info("request_id=%s trace=%s tool=%s", request_id or get_trace_id(), request_id or get_trace_id(), redact_pii(tool_name))
