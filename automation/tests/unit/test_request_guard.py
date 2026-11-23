"""请求限流与熔断器行为测试。"""

from __future__ import annotations

import httpx
import pytest

from core import (
    APIClient,
    APITransportError,
    CircuitBreaker,
    CircuitOpenError,
    RequestRateLimiter,
)

pytestmark = pytest.mark.regression


class FakeClock:
    """可同时推进 monotonic 和 sleep 的测试时钟。"""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def test_rate_limiter_enforces_minimum_interval() -> None:
    """连续请求应按照最小间隔等待。"""
    clock = FakeClock()
    limiter = RequestRateLimiter(
        0.5,
        clock=clock.monotonic,
        sleeper=clock.sleep,
    )

    limiter.wait()
    limiter.wait()
    limiter.wait()

    assert clock.sleeps == [0.5, 0.5]


def test_rate_limiter_is_disabled_at_zero_interval() -> None:
    """间隔为 0 时不执行任何等待。"""
    clock = FakeClock()
    limiter = RequestRateLimiter(
        0,
        clock=clock.monotonic,
        sleeper=clock.sleep,
    )

    limiter.wait()
    limiter.wait()

    assert clock.sleeps == []


def test_circuit_opens_after_consecutive_failures() -> None:
    """连续失败达到阈值后应拒绝请求。"""
    clock = FakeClock()
    breaker = CircuitBreaker(
        2,
        5,
        clock=clock.monotonic,
    )

    breaker.before_request(
        method="GET",
        url="https://safe.local/api/orders",
    )
    breaker.record_failure()
    breaker.record_failure()

    assert breaker.state == "open"
    assert breaker.failure_count == 2

    with pytest.raises(CircuitOpenError) as exc_info:
        breaker.before_request(
            method="GET",
            url="https://safe.local/api/orders",
        )

    assert exc_info.value.retry_after_seconds == pytest.approx(5)


def test_circuit_half_open_probe_closes_after_success() -> None:
    """恢复窗口结束后只允许一次探测，成功则关闭熔断。"""
    clock = FakeClock()
    breaker = CircuitBreaker(
        1,
        5,
        clock=clock.monotonic,
    )

    breaker.record_failure()
    clock.now = 5.0

    breaker.before_request(
        method="GET",
        url="https://safe.local/api/orders",
    )
    assert breaker.state == "half_open"

    with pytest.raises(CircuitOpenError):
        breaker.before_request(
            method="GET",
            url="https://safe.local/api/orders",
        )

    breaker.record_success()
    assert breaker.state == "closed"
    assert breaker.failure_count == 0


def test_api_client_does_not_open_circuit_for_http_500() -> None:
    """HTTP 500 表示网络可用，不计入熔断。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            json={"detail": "server error"},
            request=request,
        )

    with APIClient(
        base_url="https://safe.local",
        read_only=True,
        circuit_failure_threshold=1,
        circuit_recovery_seconds=5,
        transport=httpx.MockTransport(handler),
    ) as client:
        response = client.get("/api/orders")

        assert response.status_code == 500
        assert client.circuit_breaker.state == "closed"


def test_api_client_opens_circuit_after_transport_failures() -> None:
    """连续传输失败后，后续请求不得进入 transport。"""
    request_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_count
        request_count += 1
        raise httpx.ConnectError(
            "connection refused",
            request=request,
        )

    with APIClient(
        base_url="https://safe.local",
        read_only=True,
        circuit_failure_threshold=2,
        circuit_recovery_seconds=30,
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(APITransportError):
            client.get("/api/orders")

        with pytest.raises(APITransportError):
            client.get("/api/orders")

        assert client.circuit_breaker.state == "open"

        with pytest.raises(CircuitOpenError):
            client.get("/api/orders")

    assert request_count == 2
