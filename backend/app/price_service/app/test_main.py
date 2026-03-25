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
        "user_id": 1,
        "items": [
            {"menu_item_id": 1, "quantity": 2},
            {"menu_item_id": 2, "quantity": 1}
        ]
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["subtotal"] == pytest.approx(25.0)
    assert data["discount"] == pytest.approx(0.0)
    assert data["discounted_subtotal"] == pytest.approx(25.0)
    assert data["service_charge"] == pytest.approx(2.5)
    assert data["tax"] == pytest.approx(1.25)
    assert data["delivery_fee"] == pytest.approx(4.99)
    assert data["total"] == pytest.approx(33.74)


def test_calculate_price_with_save10():
    payload = {
        "user_id": 1,
        "items": [
            {"menu_item_id": 1, "quantity": 2},
            {"menu_item_id": 2, "quantity": 1}
        ],
        "promo_code": "SAVE10"
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["subtotal"] == pytest.approx(25.0)
    assert data["discount"] == pytest.approx(2.5)
    assert data["discounted_subtotal"] == pytest.approx(22.5)
    assert data["service_charge"] == pytest.approx(2.25)
    assert data["tax"] == pytest.approx(1.12)
    assert data["delivery_fee"] == pytest.approx(4.99)
    assert data["total"] == pytest.approx(30.87)


def test_calculate_price_with_save20():
    payload = {
        "user_id": 1,
        "items": [
            {"menu_item_id": 1, "quantity": 2},
            {"menu_item_id": 2, "quantity": 1}
        ],
        "promo_code": "SAVE20"
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["subtotal"] == pytest.approx(25.0)
    assert data["discount"] == pytest.approx(5.0)
    assert data["discounted_subtotal"] == pytest.approx(20.0)
    assert data["service_charge"] == pytest.approx(2.0)
    assert data["tax"] == pytest.approx(1.0)
    assert data["delivery_fee"] == pytest.approx(4.99)
    assert data["total"] == pytest.approx(27.99)


def test_calculate_price_with_invalid_promo():
    payload = {
        "user_id": 1,
        "items": [
            {"menu_item_id": 1, "quantity": 2},
            {"menu_item_id": 2, "quantity": 1}
        ],
        "promo_code": "BADCODE"
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200, response.json()

    data = response.json()
    assert data["discount"] == pytest.approx(0.0)
    assert data["subtotal"] == pytest.approx(25.0)
    assert data["total"] == pytest.approx(33.74)


def test_calculate_price_with_empty_items():
    payload = {
        "user_id": 1,
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
        "user_id": 1,
        "items": [
            {"menu_item_id": 1, "quantity": 0}
        ]
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 422


def test_calculate_price_with_negative_delivery_fee():
    payload = {
        "user_id": 1,
        "items": [
            {"menu_item_id": 1, "quantity": 1}
        ],
        "delivery_fee": -1
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 422


def test_calculate_price_invalid_menu_item():
    payload = {
        "user_id": 1,
        "items": [
            {"menu_item_id": 999, "quantity": 1}
        ]
    }

    response = client.post("/calculate", json=payload)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()