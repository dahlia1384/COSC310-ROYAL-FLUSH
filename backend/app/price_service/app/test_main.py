from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_calculate_price():
    payload = {
        "user_id": "1",
        "items": [
            {"menu_item_id": "1-salad", "quantity": 2},  # 17.0
            {"menu_item_id": "1-soup", "quantity": 1}    # 5.5
        ]
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["subtotal"] == pytest.approx(22.5)
    assert data["discount"] == pytest.approx(0.0)
    assert data["discounted_subtotal"] == pytest.approx(22.5)
    assert data["service_charge"] == pytest.approx(2.25)
    assert data["tax"] == pytest.approx(1.12)
    assert data["delivery_fee"] == pytest.approx(4.99)
    assert data["total"] == pytest.approx(30.87)


def test_calculate_price_with_save10():
    payload = {
        "user_id": "1",
        "items": [
            {"menu_item_id": "1-salad", "quantity": 2},
            {"menu_item_id": "1-soup", "quantity": 1}
        ],
        "promo_code": "SAVE10"
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["subtotal"] == pytest.approx(22.5)
    assert data["discount"] == pytest.approx(2.25)  # 10%
    assert data["discounted_subtotal"] == pytest.approx(20.25)
    assert data["service_charge"] == pytest.approx(2.02)
    assert data["tax"] == pytest.approx(1.01)
    assert data["delivery_fee"] == pytest.approx(4.99)
    assert data["total"] == pytest.approx(28.28)


def test_calculate_price_with_save20():
    payload = {
        "user_id": "1",
        "items": [
            {"menu_item_id": "1-salad", "quantity": 2},
            {"menu_item_id": "1-soup", "quantity": 1}
        ],
        "promo_code": "SAVE20"
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["subtotal"] == pytest.approx(22.5)
    assert data["discount"] == pytest.approx(4.5)  # 20%
    assert data["discounted_subtotal"] == pytest.approx(18.0)
    assert data["service_charge"] == pytest.approx(1.8)
    assert data["tax"] == pytest.approx(0.9)
    assert data["delivery_fee"] == pytest.approx(4.99)
    assert data["total"] == pytest.approx(25.69)


def test_calculate_price_with_invalid_promo():
    payload = {
        "user_id": "1",
        "items": [
            {"menu_item_id": "1-salad", "quantity": 2},
            {"menu_item_id": "1-soup", "quantity": 1}
        ],
        "promo_code": "BADCODE"
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["discount"] == pytest.approx(0.0)
    assert data["subtotal"] == pytest.approx(22.5)
    assert data["total"] == pytest.approx(30.87)


def test_calculate_price_with_empty_items():
    payload = {
        "user_id": "1",
        "items": []
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["subtotal"] == pytest.approx(0.0)
    assert data["discount"] == pytest.approx(0.0)
    assert data["discounted_subtotal"] == pytest.approx(0.0)
    assert data["service_charge"] == pytest.approx(0.0)
    assert data["tax"] == pytest.approx(0.0)
    assert data["delivery_fee"] == pytest.approx(4.99)
    assert data["total"] == pytest.approx(4.99)


def test_calculate_price_with_invalid_quantity():
    payload = {
        "user_id": "1",
        "items": [
            {"menu_item_id": "1-salad", "quantity": 0}
        ]
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 422


def test_calculate_price_with_negative_delivery_fee():
    payload = {
        "user_id": "1",
        "items": [
            {"menu_item_id": "1-salad", "quantity": 1}
        ],
        "delivery_fee": -1
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 422


def test_calculate_price_invalid_menu_item():
    payload = {
        "user_id": "1",
        "items": [
            {"menu_item_id": "999-does-not-exist", "quantity": 1}
        ]
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()