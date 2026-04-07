from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_restaurant_requires_auth():
    response = client.post("/restaurants", json={
        "name": "Spice House",
        "cuisine": "Indian",
        "address": "123 Main St"
    })
    assert response.status_code in [401, 422]


def test_update_restaurant_requires_auth():
    response = client.put("/restaurants/r1", json={
        "name": "Updated",
        "cuisine": "Indian",
        "address": "123 Main St",
        "rating": 4.5
    })
    assert response.status_code in [401, 422]


def test_delete_restaurant_requires_auth():
    response = client.delete("/restaurants/r1")
    assert response.status_code in [401, 422]