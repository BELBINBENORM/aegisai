import logging
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.observability.request_id import generate_request_id
from app.observability.logging import log_request
from app.observability.middleware import request_id_middleware
from app.observability.tracing import log_agent, log_tool
from app.observability.tokens import calculate_cost
from app.observability.latency import start_timer, elapsed_time
from app.observability.errors import log_error


def test_generate_request_id():
    request_id = generate_request_id()

    assert request_id
    assert len(request_id) == 36


def test_log_request(caplog):
    with caplog.at_level(logging.INFO, logger="aegisai"):
        log_request("req-123", "GET", "/health")

    assert "request_id=req-123" in caplog.text
    assert "method=GET" in caplog.text
    assert "path=/health" in caplog.text


def test_request_id_middleware():
    app = FastAPI()
    app.middleware("http")(request_id_middleware)

    @app.get("/test")
    async def test_route():
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_log_agent(caplog):
    with caplog.at_level(logging.INFO, logger="aegisai"):
        log_agent("rag_agent", "req-123")

    assert "request_id=req-123" in caplog.text
    assert "agent=rag_agent" in caplog.text


def test_log_tool(caplog):
    with caplog.at_level(logging.INFO, logger="aegisai"):
        log_tool("search", "req-123")

    assert "request_id=req-123" in caplog.text
    assert "tool=search" in caplog.text


def test_calculate_cost():
    cost = calculate_cost(
        input_tokens=1_000_000,
        output_tokens=500_000,
        input_price=1.0,
        output_price=2.0,
    )

    assert cost == 2.0


def test_latency():
    start = start_timer()
    time.sleep(0.01)

    elapsed = elapsed_time(start)

    assert elapsed >= 0.01


def test_log_error(caplog):
    error = ValueError("test error")

    with caplog.at_level(logging.ERROR, logger="aegisai"):
        log_error("req-123", error)

    assert "request_id=req-123" in caplog.text
    assert "test error" in caplog.text