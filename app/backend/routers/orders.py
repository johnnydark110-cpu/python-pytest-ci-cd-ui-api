"""订单业务模块的 CRUD 接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from .. import auth, database
from ..schemas import OrderCreate, OrderList, OrderOut, OrderUpdate

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _row_to_order(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "amount": row["amount"],
        "status": row["status"],
        "created_at": row["created_at"],
    }


@router.get("", response_model=OrderList)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    q: str | None = Query(default=None),
    current_user: dict = Depends(auth.get_current_user),
) -> OrderList:
    conn = database.get_connection()
    where = "WHERE user_id = ?"
    params: list = [current_user["id"]]
    if q:
        where += " AND title LIKE ?"
        params.append(f"%{q}%")
    total = conn.execute(
        f"SELECT COUNT(*) FROM orders {where}", params
    ).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM orders {where} ORDER BY id DESC LIMIT ? OFFSET ?",
        [*params, page_size, (page - 1) * page_size],
    ).fetchall()
    conn.close()
    return OrderList(
        total=total,
        page=page,
        page_size=page_size,
        items=[OrderOut(**_row_to_order(row)) for row in rows],
    )


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate, current_user: dict = Depends(auth.get_current_user)
) -> OrderOut:
    conn = database.get_connection()
    cursor = conn.execute(
        "INSERT INTO orders (user_id, title, amount, status) VALUES (?, ?, ?, ?)",
        (current_user["id"], payload.title, payload.amount, payload.status),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM orders WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return OrderOut(**_row_to_order(row))


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int, current_user: dict = Depends(auth.get_current_user)
) -> OrderOut:
    conn = database.get_connection()
    row = conn.execute(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (order_id, current_user["id"]),
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return OrderOut(**_row_to_order(row))


@router.put("/{order_id}", response_model=OrderOut)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    current_user: dict = Depends(auth.get_current_user),
) -> OrderOut:
    conn = database.get_connection()
    row = conn.execute(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (order_id, current_user["id"]),
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    updates = {}
    if payload.title is not None:
        updates["title"] = payload.title
    if payload.amount is not None:
        updates["amount"] = payload.amount
    if payload.status is not None:
        updates["status"] = payload.status
    if updates:
        set_clause = ", ".join(f"{key} = ?" for key in updates)
        conn.execute(
            f"UPDATE orders SET {set_clause} WHERE id = ?",
            [*updates.values(), order_id],
        )
        conn.commit()

    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    conn.close()
    return OrderOut(**_row_to_order(row))


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int, current_user: dict = Depends(auth.get_current_user)
) -> Response:
    conn = database.get_connection()
    row = conn.execute(
        "SELECT id FROM orders WHERE id = ? AND user_id = ?",
        (order_id, current_user["id"]),
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
