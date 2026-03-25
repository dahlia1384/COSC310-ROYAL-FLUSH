import app.main as main_module
from fastapi.testclient import TestClient
from app.main import app, notifications_db

client = TestClient(app)


def setup_function():
    notifications_db.clear()
    main_module.next_notification_id = 1


def test_send_general_notification():
    payload = {
        "user_id": "1",
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
        "user_id": "1",
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
    client.post("/notify-status-change", json={
        "user_id": "1",
        "order_id": 202,
        "old_status": "Preparing",
        "new_status": "Delivered"
    })

    response = client.get("/users/1/notifications")

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_mark_notification_as_read():
    create_response = client.post("/notify-status-change", json={
        "user_id": "1",
        "order_id": 202,
        "old_status": "Preparing",
        "new_status": "Delivered"
    })

    notification_id = create_response.json()["notification"]["notification_id"]

    response = client.patch(f"/notifications/{notification_id}/read")

    assert response.status_code == 200
    assert response.json()["status"] == "notification marked as read"
    assert response.json()["notification"]["is_read"] is True


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert "running" in response.json()["message"].lower()


def test_get_user_notifications_empty():
    response = client.get("/users/123/notifications")

    assert response.status_code == 200
    assert response.json()["count"] == 0
    assert response.json()["notifications"] == []


def test_get_unread_notifications():
    client.post("/notify-new-order", json={
        "manager_id": 99,
        "order_id": 202,
        "customer_id": 7
    })

    response = client.get("/users/99/notifications/unread")

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["notifications"][0]["is_read"] is False


def test_unread_notifications_after_mark_read():
    create_response = client.post("/notify-new-order", json={
        "manager_id": 99,
        "order_id": 202,
        "customer_id": 7
    })

    notification_id = create_response.json()["notification"]["notification_id"]

    client.patch(f"/notifications/{notification_id}/read")

    response = client.get("/users/99/notifications/unread")

    assert response.status_code == 200
    assert response.json()["count"] == 0
    assert response.json()["notifications"] == []


def test_mark_notification_as_read_missing_notification():
    response = client.patch("/notifications/999/read")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_send_general_notification_missing_message():
    payload = {
        "user_id": "1",
        "title": "Order Update",
        "message": "",
        "type": "general"
    }

    response = client.post("/send-general", json=payload)

    assert response.status_code == 422


def test_notify_status_change_missing_new_status():
    payload = {
        "user_id": "1",
        "order_id": 101,
        "old_status": "Preparing",
        "new_status": ""
    }

    response = client.post("/notify-status-change", json=payload)

    assert response.status_code == 422


def test_notify_new_order_with_custom_message():
    payload = {
        "manager_id": 99,
        "order_id": 202,
        "customer_id": 7,
        "message": "A new priority order has been placed."
    }

    response = client.post("/notify-new-order", json=payload)

    assert response.status_code == 200
    assert response.json()["notification"]["message"] == "A new priority order has been placed."


def test_multiple_notifications_for_same_user():
    client.post("/notify-new-order", json={
        "manager_id": 99,
        "order_id": 202,
        "customer_id": 7
    })
    client.post("/notify-new-order", json={
        "manager_id": 99,
        "order_id": 203,
        "customer_id": 8
    })

    response = client.get("/users/99/notifications")

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert len(response.json()["notifications"]) == 2


def test_notification_ids_increment():
    first = client.post("/notify-new-order", json={
        "manager_id": 99,
        "order_id": 202,
        "customer_id": 7
    })
    second = client.post("/notify-new-order", json={
        "manager_id": 99,
        "order_id": 203,
        "customer_id": 8
    })

    first_id = first.json()["notification"]["notification_id"]
    second_id = second.json()["notification"]["notification_id"]

    assert second_id == first_id + 1