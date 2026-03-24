import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_delivery():
    payload = {
        "order_id": "testid1",
        "restaurant_id": 1,
        "delivery_method": "Car" }

    assert response.status_code ==200
    data = response.json()
    assert data["order_id"] == "testid1"
    assert data["delivery_status"] == "Preparing Order"
    assert data["delivery_method"] == "Car"

def test_get_delivery():
    payload = {
        "order_id": "testid2",
        "restaurant_id": 1,
        "delivery_method": "Bike" }

    response = client.get("/deliveries/testid2")
    assert response.status_code == 404

def test_get_delivery_not_found():
    response = client.get("/deliveries/doesnotexist")
    assert response.status_code == 404

def test_update_delivery__status():
    payload = {
        "order_id": "testid3",
        "restaurant_id": 1,
        "delivery_method": "Walk" }

    response = client.put("/deliveries/testid3/status", json={"delivery_status": "Order Delivered"})
    assert response.status_code == 404

def test_update_delivery_status_blocked():
    payload = {
        "order_id": "testid4",
        "restaurant_id": 1,
        "delivery_method": "Car" }

    client.put("/deliveries/testid4/status", json={"delivery_status": "Order Delivered"})
    response = client.put("/deliveries/testid4/status", json={"delivery_status": "Preparing Order"})
    assert response.status_code == 404
    