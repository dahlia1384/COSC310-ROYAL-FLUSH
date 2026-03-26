import pytest
from fastapi import HTTPException
from uuid import UUID

from app.schemas.order_schema import OrderCreate
from app.services import order_services


VALID_PAYLOAD = {
    "restaurant_id": "1",
    "customer_id": "ac8fc3f0-d128-4ffa-a5b1-6b803746a392",
    "items": [{"menu_item_id": "101", "quantity": 2}],
    "delivery_method": "car"
}


def test_schema_valid():
    order = OrderCreate(**VALID_PAYLOAD)
    assert isinstance(order.customer_id, str)
    assert len(order.items) == 1
    assert order.items[0].quantity == 2


def test_schema_invalid_quantity():
    bad_payload = VALID_PAYLOAD.copy()
    bad_payload["items"] = [{"menu_item_id": "101", "quantity": 0}]

    with pytest.raises(Exception):
        OrderCreate(**bad_payload)


def test_create_order(monkeypatch):
    monkeypatch.setattr(
        order_services,
        "create_order",
        lambda x: {**x, "order_time": "2024-04-12T00:00:00"},
    )

    order = order_services.create_new_order(OrderCreate(**VALID_PAYLOAD))

    assert order.order_status == "Pending Payment"
    assert isinstance(order.customer_id, str)
    assert order.order_time.isoformat() == "2024-04-12T00:00:00"


def test_get_order(monkeypatch):
    fake_order = {
        "order_id": "c65a8a1",
        **VALID_PAYLOAD,
        "order_status": "Order Created",
        "order_time": "2024-04-12T00:00:00",
    }

    monkeypatch.setattr(order_services, "get_order_by_id", lambda x: fake_order)

    order = order_services.get_order("c65a8a1")
    assert order.order_id == "c65a8a1"


def test_get_order_not_found(monkeypatch):
    monkeypatch.setattr(order_services, "get_order_by_id", lambda x: None)

    with pytest.raises(HTTPException) as exc_info:
        order_services.get_order("missing")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order Not Found"


def test_change_status(monkeypatch):
    fake_order = {
        "order_id": "c65a8a1",
        **VALID_PAYLOAD,
        "order_status": "Preparing Order",
        "order_time": "2024-04-12T00:00:00",
    }

    monkeypatch.setattr(order_services, "get_order_by_id", lambda x: fake_order)
    monkeypatch.setattr(
        order_services,
        "update_order_status",
        lambda order_id, status: {**fake_order, "order_status": status},
    )

    updated = order_services.change_order_status("c65a8a1", "Order Delivered")
    assert updated.order_status == "Order Delivered"


def test_change_status_block_delivered(monkeypatch):
    fake_order = {
        "order_id": "c65a8a1",
        **VALID_PAYLOAD,
        "order_status": "Order Delivered",
        "order_time": "2024-04-12T00:00:00",
    }

    monkeypatch.setattr(order_services, "get_order_by_id", lambda x: fake_order)

    with pytest.raises(HTTPException) as exc_info:
        order_services.change_order_status("c65a8a1", "Preparing Order")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Can't modify delivered order"