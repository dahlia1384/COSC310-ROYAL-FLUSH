import app.main as main_module
from fastapi.testclient import TestClient
from app.main import app, notifications_db

client = TestClient(app)


def setup_function():
    notifications_db.clear()
    main_module.next_notification_id = 1


def test_send_general_notification():
    payload = {
        "user_id": 1,
        "title": "Order Update",
        "message": "Your order is ready",
        "type": "general"
    }

    response = client.post("/send-general", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["user_id"] == 1
    assert response.json()["notification"]["message"] == "Your order is ready"


def test_notify_status_change():
    payload = {
        "user_id": 1,
        "order_id": 101,
        "old_status": "Preparing",
        "new_status": "Out for Delivery"
    }

    response = client.post("/notify-status-change", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["type"] == "order_status_update"


def test_notify_new_order_manager_alert():
    payload = {
        "manager_id": 99,
        "order_id": 202,
        "customer_id": 7
    }

    response = client.post("/notify-new-order", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["user_id"] == 99
    assert response.json()["notification"]["type"] == "manager_new_order_alert"
    assert response.json()["notification"]["order_id"] == 202


def test_get_user_notifications():
    client.post("/notify-new-order", json={
        "manager_id": 99,
        "order_id": 202,
        "customer_id": 7
    })

    response = client.get("/users/99/notifications")

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_mark_notification_as_read():
    create_response = client.post("/notify-new-order", json={
        "manager_id": 99,
        "order_id": 202,
        "customer_id": 7
    })

    notification_id = create_response.json()["notification"]["notification_id"]

    response = client.patch(f"/notifications/{notification_id}/read")

    assert response.status_code == 200
    assert response.json()["status"] == "notification marked as read"
    assert response.json()["notification"]["is_read"] is True