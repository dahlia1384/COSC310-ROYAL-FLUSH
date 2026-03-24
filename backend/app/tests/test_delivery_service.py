import pytest
from fastapi import HTTPException
from app.services import delivery_services

VALID_ORDER = {
        "order_id": "c65a8aL",
        "restaurant_id": 1,
        "delivery_method": "Car" }

def test_create_delivery(monkeypatch):
    monkeypatch.setattr(delivery_services,"create_delivery",lambda x: {**x, "delivery_time": "2024-04-12T00:00:00"})
    delivery = delivery_services.create_new_delivery(VALID_ORDER)
    assert delivery.order_id == "c65a8aL"
    assert delivery.delivery_status == "Preparing Order"
    assert delivery.delivery_method == "Car"
    assert delivery.delivery_time.isoformat() == "2024-04-12T00:00:00"

def test_get_delivery(monkeypatch):
    fake_delivery = {
        "order_id": "c65a8aL",
        "restaurant_id": 1,
        "delivery_status": "Preparing Order",
        "delivery_method": "Car",
        "delivery_time": "2024-04-12T00:00:00"}
    
    monkeypatch.setattr(delivery_services, "get_delivery_by_order_id", lambda x: fake_delivery)
    delivery = delivery_services.get_delivery("c65a8aL")
    assert delivery.order_id == "c65a8aL"


def test_get_delivery_not_found(monkeypatch):
    monkeypatch.setattr(delivery_services, "get_delivery_by_order_id", lambda x: None)
    with pytest.raises(HTTPException):
        delivery_services.get_delivery("invalid_id")

def test_change_delivery_status(monkeypatch):
    fake_delivery = {
        "order_id": "c65a8aL",
        "restaurant_id": 1,
        "delivery_status": "Preparing Order",
        "delivery_method": "Car",
        "delivery_time": "2024-04-12T00:00:00"}

    monkeypatch.setattr(delivery_services, "get_delivery_by_order_id", lambda x: fake_delivery)
    monkeypatch.setattr(delivery_services, "update_delivery_status", lambda order_id,status: {**fake_delivery, "delivery_status": status})
    updated = delivery_services.change_delivery_status("c65a8aL", "Order Delivered")
    assert updated.delivery_status == "Order Delivered"

def test_change_delivery_status_block_delivered(monkeypatch):
    fake_delivery = {
        "order_id": "c65a8aL",
        "restaurant_id": 1,
        "delivery_status": "Order Delivered",
        "delivery_method": "Car",
        "delivery_time": "2024-04-12T00:00:00"}

    monkeypatch.setattr(delivery_services, "get_delivery_by_order_id", lambda x: fake_delivery)
    with pytest.raises(HTTPException):
        delivery_services.change_delivery_status("c65a8aL", "Preparing Order") 

