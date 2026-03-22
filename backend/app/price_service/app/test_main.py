from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

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
    assert data["tax"] == pytest.approx(1.25)
    assert data["delivery_fee"] == pytest.approx(4.99)
