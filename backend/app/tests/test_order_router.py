from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "restaurant_id": "1",
    "customer_id": "ac8fc3f0-d128-4ffa-a5b1-6b803746a392",
    "items": [{"menu_item_id": "101", "quantity": 2}],
    "delivery_method": "car"
}

def test_create_order():
    response = client.post("/orders/", json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert str(data["order_id"]) != ""
    assert data["order_status"] == "Pending Payment"


def test_get_order():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert str(response.json()["order_id"]) == order_id

def test_get_order_not_found():
    response = client.get("/orders/invalid")
    assert response.status_code == 404

def test_create_order_empty_items():
    bad_payload = VALID_PAYLOAD.copy()
    bad_payload["items"] = []
    response = client.post("/orders/", json=bad_payload)
    assert response.status_code == 422

def test_update_order_status():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])
    response = client.put(f"/orders/{order_id}/status", json={"order_status": "Order Delivered"})
    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == "Order Delivered"

def test_update_order_status_invalid_payload():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])
    response = client.put( f"/orders/{order_id}/status", json={})
    assert response.status_code == 422

def test_update_order_status_blocked():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])
    client.put(f"/orders/{order_id}/status", json={"order_status": "Order Delivered"})
    response = client.put(f"/orders/{order_id}/status", json={"order_status": "Preparing Order"})
    assert response.status_code == 400

def test_pay_order_success(monkeypatch):
    monkeypatch.setattr("app.services.payment_service._calculate_total", lambda order, promo_code=None: 25.5)

    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])

    response = client.post(
        f"/orders/{order_id}/pay",
        json={
            "customer_id": VALID_PAYLOAD["customer_id"],
            "payment_method": "credit_card",
            "simulate_success": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["customer_id"] == VALID_PAYLOAD["customer_id"]
    assert data["payment_status"] == "success"
    assert data["order_status"] == "Paid"


def test_pay_order_not_found():
    response = client.post(
        "/orders/invalid/pay",
        json={
            "customer_id": VALID_PAYLOAD["customer_id"],
            "payment_method": "credit_card",
            "simulate_success": True
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_pay_order_wrong_customer():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])

    response = client.post(
        f"/orders/{order_id}/pay",
        json={
            "customer_id": "wrong-customer-id",
            "payment_method": "credit_card",
            "simulate_success": True
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to pay for this order"


def test_pay_order_invalid_payment_method():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])

    response = client.post(
        f"/orders/{order_id}/pay",
        json={
            "customer_id": VALID_PAYLOAD["customer_id"],
            "payment_method": "bitcoin",
            "simulate_success": True
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid payment method"