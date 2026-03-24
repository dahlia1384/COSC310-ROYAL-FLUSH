from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_delivery():
    response = client.get("/deliveries/testid2")
    assert response.status_code == 404


def test_get_delivery_not_found():
    response = client.get("/deliveries/doesnotexist")
    assert response.status_code == 404


def test_update_delivery_status():
    response = client.put("/deliveries/testid3/status",json={"delivery_status": "Order Delivered"})
    assert response.status_code == 404


def test_update_delivery_status_blocked():
    client.put("/deliveries/testid4/status",json={"delivery_status": "Order Delivered"})
    response = client.put("/deliveries/testid4/status",json={"delivery_status": "Preparing Order"})
    assert response.status_code == 404