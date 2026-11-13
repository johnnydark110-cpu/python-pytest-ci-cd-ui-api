"""被测系统冒烟自测：验证前后端核心流程可用。"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.backend.main import app


def main() -> None:
    username = "u" + uuid.uuid4().hex[:8]
    password = "secret123"

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "订单管理系统" in response.text
        print("GET / ->", response.status_code)

        response = client.post(
            "/api/auth/register",
            json={"username": username, "password": password},
        )
        print("register ->", response.status_code)
        assert response.status_code == 201
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/orders",
            json={"title": "测试订单A", "amount": 99.5, "status": "pending"},
            headers=headers,
        )
        print("create ->", response.status_code)
        assert response.status_code == 201
        order_id = response.json()["id"]

        response = client.get("/api/orders", headers=headers)
        print("list ->", response.status_code, "total =", response.json()["total"])
        assert response.status_code == 200
        assert response.json()["total"] >= 1

        response = client.get(f"/api/orders/{order_id}", headers=headers)
        print("get ->", response.status_code, "title =", response.json()["title"])
        assert response.status_code == 200

        response = client.put(
            f"/api/orders/{order_id}", json={"status": "paid"}, headers=headers
        )
        print("update ->", response.status_code, "status =", response.json()["status"])
        assert response.status_code == 200
        assert response.json()["status"] == "paid"

        response = client.get("/api/orders")
        print("unauthorized ->", response.status_code)
        assert response.status_code == 401

        response = client.delete(f"/api/orders/{order_id}", headers=headers)
        print("delete ->", response.status_code)
        assert response.status_code == 204

    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
