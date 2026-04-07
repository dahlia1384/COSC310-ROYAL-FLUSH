from fastapi.testclient import TestClient
from app.services import order_services
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "restaurant_id": "1",
    "customer_id": "ac8fc3f0-d128-4ffa-a5b1-6b803746a392",
    "items": [{"menu_item_id": "101", "quantity": 2}],
    "delivery_method": "car",
    "customer_city": "City_3"
}

def mock_available_menu_item(monkeypatch):
    available_item = type("MenuItemObj", (), {
        "id": "101",
        "name": "Mock Menu Item",
        "available": True,
    })()
    monkeypatch.setattr(order_services, "get_menu_item_by_id", lambda menu_item_id: available_item)

def test_create_order(monkeypatch):
    from app.services import order_services

    available_item = type("MenuItemObj", (), {
        "id": "101",
        "name": "Mock Item",
        "available": True,
    })()

    monkeypatch.setattr(order_services, "get_menu_item_by_id", lambda menu_item_id: available_item)

    response = client.post("/orders/", json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert str(data["order_id"]) != ""
    assert data["order_status"] == "Pending Payment"

def test_create_order_rejects_unavailable_menu_item(monkeypatch):
    from app.services import order_services

    unavailable_item = type("MenuItemObj", (), {
        "id": "101",
        "name": "Paneer Tikka",
        "available": False,
    })()

    monkeypatch.setattr(order_services, "get_menu_item_by_id", lambda menu_item_id: unavailable_item)

    response = client.post("/orders/", json=VALID_PAYLOAD)

    assert response.status_code == 400
    assert "unavailable" in response.json()["detail"].lower()

def test_get_order(monkeypatch):
    mock_available_menu_item(monkeypatch)

    create = client.post("/orders/", json=VALID_PAYLOAD)
    assert create.status_code == 201, create.json()

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

def test_update_order_status(monkeypatch):
    mock_available_menu_item(monkeypatch)

    create = client.post("/orders/", json=VALID_PAYLOAD)
    assert create.status_code == 201, create.json()

    order_id = str(create.json()["order_id"])
    response = client.put(f"/orders/{order_id}/status", json={"order_status": "Order Delivered"})

    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == "Order Delivered"

def test_update_order_status_invalid_payload(monkeypatch):
    mock_available_menu_item(monkeypatch)

    create = client.post("/orders/", json=VALID_PAYLOAD)
    assert create.status_code == 201, create.json()

    order_id = str(create.json()["order_id"])
    response = client.put( f"/orders/{order_id}/status", json={})

    assert response.status_code == 422

def test_update_order_status_blocked(monkeypatch):
    mock_available_menu_item(monkeypatch)

    create = client.post("/orders/", json=VALID_PAYLOAD)
    assert create.status_code == 201, create.json()

    order_id = str(create.json()["order_id"])
    client.put(f"/orders/{order_id}/status", json={"order_status": "Order Delivered"})
    response = client.put(f"/orders/{order_id}/status", json={"order_status": "Preparing Order"})
    assert response.status_code == 400

def test_pay_order_success(monkeypatch):
    mock_available_menu_item(monkeypatch)

    monkeypatch.setattr("app.services.payment_service._calculate_total", lambda order, promo_code=None: 25.5)

    create = client.post("/orders/", json=VALID_PAYLOAD)
    assert create.status_code == 201, create.json()
    
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


def test_pay_order_wrong_customer(monkeypatch):
    mock_available_menu_item(monkeypatch)
    create = client.post("/orders/", json=VALID_PAYLOAD)
    assert create.status_code == 201, create.json()

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


def test_pay_order_invalid_payment_method(monkeypatch):
    mock_available_menu_item(monkeypatch)
    create = client.post("/orders/", json=VALID_PAYLOAD)
    assert create.status_code == 201, create.json()

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