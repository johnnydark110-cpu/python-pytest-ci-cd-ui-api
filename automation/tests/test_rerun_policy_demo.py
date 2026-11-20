"""临时用：验证重试只作用于网络传输异常。"""

import httpx
import pytest

from core import APITransportError

attempts = {
    "assertion": 0,
    "transport": 0,
}
"""
这个标记等价于给**当前文件所有测试函数**加上这个重试规则：

- `reruns=2`：最多重试 2 次（第一次失败 + 重试 2 次，一共最多执行 3 次）
- `reruns_delay=1`：每次重试之间等待 1 秒
- `only_rerun=["APITransportError"]`：**重中之重**
✅ 只有抛出 `APITransportError` 才触发重试
❌ 别的报错（AssertionError、普通异常）一概不重试，直接失败

> 
> `pytestmark` 是文件级标记，不用每个函数单独写 `@pytest.mark.flaky`
"""
pytestmark = pytest.mark.flaky(
    reruns=2,
    reruns_delay=1,
    only_rerun=["APITransportError"],
)


def test_assertion_error_is_not_rerun() -> None:
    """普通断言失败应立即结束，不允许重试。"""
    attempts["assertion"] += 1

    assert attempts["assertion"] == 2, f"assertion_attempt={attempts['assertion']}"


def test_transport_error_is_retried() -> None:
    """模拟前两次网络传输失败，第三次应成功。"""
    attempts["transport"] += 1

    if attempts["transport"] < 3:
        raise APITransportError(
            method="GET",
            url="http://127.0.0.1:9999/health",
            cause=httpx.ConnectError("模拟网络连接失败"),
        )

    assert attempts["transport"] == 3
