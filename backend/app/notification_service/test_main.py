from fastapi.testclient import TestClient
from app.main import app, notifications_db, preferences_db

client = TestClient(app)


def setup_function():
    notifications_db.clear()
    preferences_db.clear()


def test_get_default_preferences():
    response = client.get("/users/1/preferences")

    assert response.status_code == 200
    assert response.json()["user_id"] == 1
    assert response.json()["order_status_updates"] is True
    assert response.json()["promotions"] is True
    assert response.json()["general_notifications"] is True


def test_update_preferences():
    response = client.put("/users/1/preferences", json={
        "order_status_updates": False,
        "promotions": False
    })

    assert response.status_code == 200
    assert response.json()["status"] == "preferences updated"
    assert response.json()["preferences"]["order_status_updates"] is False
    assert response.json()["preferences"]["promotions"] is False
    assert response.json()["preferences"]["general_notifications"] is True


def test_status_notification_blocked_by_preferences():
    client.put("/users/1/preferences", json={
        "order_status_updates": False
    })

    response = client.post("/notify-status-change", json={
        "user_id": 1,
        "order_id": 101,
        "old_status": "Preparing",
        "new_status": "Delivered"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "notification blocked by user preferences"


def test_status_notification_sent_when_enabled():
    response = client.post("/notify-status-change", json={
        "user_id": 1,
        "order_id": 101,
        "old_status": "Preparing",
        "new_status": "Delivered"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["type"] == "order_status_update"


def test_promo_notification_blocked_by_preferences():
    client.put("/users/1/preferences", json={
        "promotions": False
    })

    response = client.post("/send-general", json={
        "user_id": 1,
        "title": "Promo",
        "message": "You got 10 percent off",
        "type": "promo_update"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "notification blocked by user preferences"