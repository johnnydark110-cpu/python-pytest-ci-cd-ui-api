"""APIClient 请求节流与连续传输失败熔断。"""

from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from time import monotonic, sleep
from typing import Literal

from .exceptions import CircuitOpenError

CircuitState = Literal["closed", "open", "half_open"]


class RequestRateLimiter:
    """限制同一客户端相邻请求的最小时间间隔。"""

    def __init__(
        self,
        minimum_interval_seconds: float,
        *,
        clock: Callable[[], float] = monotonic,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if minimum_interval_seconds < 0:
            raise ValueError("minimum_interval_seconds 不能小于 0")

        self.minimum_interval_seconds = minimum_interval_seconds
        self._clock = clock
        self._sleeper = sleeper
        self._next_allowed_at = 0.0
        self._lock = Lock()

    def wait(self) -> None:
        """必要时等待，确保相邻请求满足最小间隔。"""
        if self.minimum_interval_seconds == 0:
            return

        with self._lock:
            now = self._clock()
            delay = max(0.0, self._next_allowed_at - now)

            if delay > 0:
                self._sleeper(delay)

            now = self._clock()
            self._next_allowed_at = (
                max(now, self._next_allowed_at) + self.minimum_interval_seconds
            )


class CircuitBreaker:
    """连续传输失败达到阈值后阻止后续网络请求。"""

    def __init__(
        self,
        failure_threshold: int,
        recovery_seconds: float,
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold 必须大于等于 1")

        if recovery_seconds <= 0:
            raise ValueError("recovery_seconds 必须大于 0")

        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self._clock = clock
        self._failure_count = 0
        self._opened_at: float | None = None
        self._state: CircuitState = "closed"
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        """返回当前熔断状态。"""
        with self._lock:
            return self._state

    @property
    def failure_count(self) -> int:
        """返回当前连续传输失败次数。"""
        with self._lock:
            return self._failure_count

    def before_request(
        self,
        *,
        method: str,
        url: str,
    ) -> None:
        """允许请求通过，或在熔断期间直接拒绝。"""
        with self._lock:
            now = self._clock()

            if self._state == "open":
                opened_at = self._opened_at if self._opened_at is not None else now
                elapsed = now - opened_at
                remaining = self.recovery_seconds - elapsed

                if remaining > 0:
                    raise CircuitOpenError(
                        method=method,
                        url=url,
                        retry_after_seconds=remaining,
                    )

                self._state = "half_open"
                return

            if self._state == "half_open":
                raise CircuitOpenError(
                    method=method,
                    url=url,
                    retry_after_seconds=0.0,
                )

    def record_success(self) -> None:
        """收到任意 HTTP 响应后恢复为闭合状态。"""
        with self._lock:
            self._state = "closed"
            self._failure_count = 0
            self._opened_at = None

    def record_failure(self) -> None:
        """记录一次网络传输失败，必要时打开熔断器。"""
        with self._lock:
            self._failure_count += 1
            now = self._clock()

            if (
                self._state == "half_open"
                or self._failure_count >= self.failure_threshold
            ):
                self._state = "open"
                self._opened_at = now
