from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_send_notification():
    payload = {
        "user_id": 1,
        "message": "Your order is ready"
    }

    response = client.post("/send", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"