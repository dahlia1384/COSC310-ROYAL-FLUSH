import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

import main as notification_module

app = notification_module.app
notifications_db = notification_module.notifications_db
preferences_db = notification_module.preferences_db

client = TestClient(app)


def setup_function(function):
    notifications_db.clear()
    preferences_db.clear()
    notification_module.next_notification_id = 1


def create_general_notification(
    user_id=1,
    title="Order Update",
    message="Your order is ready",
    notification_type="general",
):
    return client.post(
        "/send-general",
        json={
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type,
        },
    )


def create_status_notification(
    user_id=1,
    order_id=101,
    old_status="Preparing",
    new_status="Out for Delivery",
):
    return client.post(
        "/notify-status-change",
        json={
            "user_id": user_id,
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
        },
    )


def create_manager_alert(
    manager_id=99,
    order_id=202,
    customer_id=7,
    message=None,
):
    payload = {
        "manager_id": manager_id,
        "order_id": order_id,
        "customer_id": customer_id,
    }
    if message is not None:
        payload["message"] = message

    return client.post("/notify-new-order", json=payload)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"].lower()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_send_general_notification():
    response = create_general_notification()

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["user_id"] == 1
    assert response.json()["notification"]["message"] == "Your order is ready"
    assert response.json()["notification"]["type"] == "general"


def test_notify_status_change():
    response = create_status_notification()

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["type"] == "order_status_update"
    assert response.json()["notification"]["order_id"] == 101


def test_notify_new_order_manager_alert():
    response = create_manager_alert()

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["user_id"] == 99
    assert response.json()["notification"]["type"] == "manager_new_order_alert"
    assert response.json()["notification"]["order_id"] == 202


def test_notify_new_order_with_custom_message():
    response = create_manager_alert(message="A new priority order has been placed.")

    assert response.status_code == 200
    assert response.json()["notification"]["message"] == "A new priority order has been placed."


def test_get_user_notifications():
    create_manager_alert()

    response = client.get("/users/99/notifications")

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert len(response.json()["notifications"]) == 1


def test_get_user_notifications_empty():
    response = client.get("/users/123/notifications")

    assert response.status_code == 200
    assert response.json()["count"] == 0
    assert response.json()["notifications"] == []


def test_get_unread_notifications():
    create_manager_alert()

    response = client.get("/users/99/notifications/unread")

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["notifications"][0]["is_read"] is False


def test_mark_notification_as_read():
    create_response = create_manager_alert()
    notification_id = create_response.json()["notification"]["notification_id"]

    response = client.patch(f"/notifications/{notification_id}/read")

    assert response.status_code == 200
    assert response.json()["status"] == "notification marked as read"
    assert response.json()["notification"]["is_read"] is True


def test_unread_notifications_after_mark_read():
    create_response = create_manager_alert()
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


def test_get_default_preferences():
    response = client.get("/users/1/preferences")

    assert response.status_code == 200
    assert response.json()["user_id"] == 1
    assert response.json()["order_status_updates"] is True
    assert response.json()["promotions"] is True
    assert response.json()["general_notifications"] is True


def test_update_preferences():
    response = client.put(
        "/users/1/preferences",
        json={
            "order_status_updates": False,
            "promotions": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "preferences updated"
    assert response.json()["preferences"]["order_status_updates"] is False
    assert response.json()["preferences"]["promotions"] is False
    assert response.json()["preferences"]["general_notifications"] is True


def test_status_notification_blocked_by_preferences():
    client.put("/users/1/preferences", json={"order_status_updates": False})

    response = create_status_notification(user_id=1, new_status="Delivered")

    assert response.status_code == 200
    assert response.json()["status"] == "notification blocked by user preferences"


def test_status_notification_sent_when_enabled():
    response = create_status_notification(user_id=1, new_status="Delivered")

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["type"] == "order_status_update"


def test_promo_notification_blocked_by_preferences():
    client.put("/users/1/preferences", json={"promotions": False})

    response = create_general_notification(
        user_id=1,
        title="Promo",
        message="You got 10 percent off",
        notification_type="promo_update",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "notification blocked by user preferences"


def test_general_notification_blocked_by_preferences():
    client.put("/users/1/preferences", json={"general_notifications": False})

    response = create_general_notification(
        user_id=1,
        title="Reminder",
        message="General notification test",
        notification_type="general",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "notification blocked by user preferences"


def test_multiple_notifications_for_same_user():
    create_manager_alert(order_id=202, customer_id=7)
    create_manager_alert(order_id=203, customer_id=8)

    response = client.get("/users/99/notifications")

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert len(response.json()["notifications"]) == 2


def test_notification_ids_increment():
    first = create_manager_alert(order_id=202, customer_id=7)
    second = create_manager_alert(order_id=203, customer_id=8)

    first_id = first.json()["notification"]["notification_id"]
    second_id = second.json()["notification"]["notification_id"]

    assert second_id == first_id + 1