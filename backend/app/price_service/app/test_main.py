from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

def test_calculate_price():
    payload = {
        "user_id": 1,
        "items": [
            {"name": "Burger", "price": 10.0, "quantity": 2},
            {"name": "Fries", "price": 5.0, "quantity": 1}
        ]
    }

    response = client.post("/calculate", json=payload)
    print(response.status_code)
    print(response.json())

    assert response.status_code == 200

    data = response.json()
    assert data["subtotal"] == 25.0
    assert data["tax"] == 1.25
    assert data["delivery_fee"] == 4.99
    assert data["total"] == 31.24