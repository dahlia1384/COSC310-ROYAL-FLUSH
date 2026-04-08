from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_menu_item_requires_auth():
    response = client.post("/restaurants/r1/menu-items", json={
        "name": "Butter Chicken",
        "price": 15.5,
        "description": "classic dish"
    })
    assert response.status_code in [401, 422]


def test_update_menu_item_requires_auth():
    response = client.put("/menu-items/m1", json={
        "name": "Butter Paneer",
        "price": 16.0,
        "description": "vegetarian option"
    })
    assert response.status_code in [401, 422]


def test_delete_menu_item_requires_auth():
    response = client.delete("/menu-items/m1")
    assert response.status_code in [401, 422]