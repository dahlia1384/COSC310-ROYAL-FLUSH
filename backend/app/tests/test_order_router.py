from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
        "restaurant_id": 1,
        "customer_id": "ac8fc3f0-d128-4ffa-a5b1-6b803746a392",
        "items":[{ "menu_item_id": 101, "quantity": 2}]
}
def test_create_order():
    response = client.post("/orders/", json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["order_status"] == "Order Created"

def test_get_order():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["order_id"] == order_id

def test_get_order_not_found():
    response = client.get("/orders/invalid")
    assert response.status_code == 404

def test_update_order_status():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])
    response = client.put(f"/orders/{order_id}/status",json={"status": "Order Delivered"})
    assert response.status_code == 200
    assert response.json()["order_status"] == "Order Delivered"

def test_update_order_status_blocked():
    create = client.post("/orders/", json=VALID_PAYLOAD)
    order_id = str(create.json()["order_id"])
    client.put(f"/orders/{order_id}/status", json={"status": "Order Delivered"})
    response = client.put(f"/orders/{order_id}/status",json={"status": "Preparing Order"})
    assert response.status_code == 400






    