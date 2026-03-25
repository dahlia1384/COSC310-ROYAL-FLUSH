from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)


def post_calculate(payload: dict):
    return client.post("/calculate", json=payload)


def assert_price_response(
    data,
    subtotal,
    discount,
    discounted_subtotal,
    service_charge,
    tax,
    delivery_fee,
    total,
):
    assert data["subtotal"] == pytest.approx(subtotal)
    assert data["discount"] == pytest.approx(discount)
    assert data["discounted_subtotal"] == pytest.approx(discounted_subtotal)
    assert data["service_charge"] == pytest.approx(service_charge)
    assert data["tax"] == pytest.approx(tax)
    assert data["delivery_fee"] == pytest.approx(delivery_fee)
    assert data["total"] == pytest.approx(total)


def base_payload():
    return {
        "user_id": "1",
        "items": [
            {"menu_item_id": 1, "quantity": 2},
            {"menu_item_id": 2, "quantity": 1}
        ]
    }


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_calculate_price():
    response = post_calculate(base_payload())
    assert response.status_code == 200
    data = response.json()
    assert_price_response(data, 25.0, 0.0, 25.0, 2.5, 1.25, 4.99, 33.74)


def test_calculate_price_with_save10():
    payload = base_payload()
    payload["promo_code"] = "SAVE10"
    response = post_calculate(payload)
    assert response.status_code == 200
    data = response.json()
    assert_price_response(data, 25.0, 2.5, 22.5, 2.25, 1.12, 4.99, 30.87)


def test_calculate_price_with_save20():
    payload = base_payload()
    payload["promo_code"] = "SAVE20"
    response = post_calculate(payload)
    assert response.status_code == 200
    data = response.json()
    assert_price_response(data, 25.0, 5.0, 20.0, 2.0, 1.0, 4.99, 27.99)


def test_calculate_price_with_invalid_promo():
    payload = base_payload()
    payload["promo_code"] = "BADCODE"
    response = post_calculate(payload)
    assert response.status_code == 200
    data = response.json()
    assert_price_response(data, 25.0, 0.0, 25.0, 2.5, 1.25, 4.99, 33.74)


def test_calculate_price_with_lowercase_promo():
    payload = base_payload()
    payload["promo_code"] = "save10"
    response = post_calculate(payload)
    assert response.status_code == 200
    data = response.json()
    assert data["discount"] == pytest.approx(2.5)
    assert data["total"] == pytest.approx(30.87)


def test_calculate_price_with_empty_items():
    payload = {"user_id": "1", "items": []}
    response = post_calculate(payload)
    assert response.status_code == 200
    data = response.json()
    assert_price_response(data, 0.0, 0.0, 0.0, 0.0, 0.0, 4.99, 4.99)


def test_calculate_price_with_invalid_quantity():
    payload = {"user_id": "1", "items": [{"menu_item_id": 1, "quantity": 0}]}
    response = post_calculate(payload)
    assert response.status_code == 422


def test_calculate_price_with_negative_delivery_fee():
    payload = {"user_id": "1", "items": [{"menu_item_id": 1, "quantity": 1}], "delivery_fee": -1}
    response = post_calculate(payload)
    assert response.status_code == 422


def test_calculate_price_invalid_menu_item():
    payload = {"user_id": "1", "items": [{"menu_item_id": 999, "quantity": 1}]}
    response = post_calculate(payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_response_contains_item_breakdown():
    response = post_calculate(base_payload())
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert "menu_item_id" in data["items"][0]
    assert "quantity" in data["items"][0]
    assert "unit_price" in data["items"][0]
    assert "line_total" in data["items"][0]