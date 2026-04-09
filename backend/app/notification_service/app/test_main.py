from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import main
from main import router, notifications_db, preferences_db

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def setup_function():
    notifications_db.clear()
    preferences_db.clear()
    main.next_notification_id = 1


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
    assert response.json()["notification"]["user_id"] == "1"
    assert response.json()["notification"]["message"] == "Your order is ready"


def test_notify_status_change():
    payload = {
        "user_id": "1",
        "order_id": "101",
        "old_status": "Preparing",
        "new_status": "Out for Delivery"
    }

    response = client.post("/notify-status-change", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["type"] == "order_status_update"


def test_notify_new_order_manager_alert():
    payload = {
        "manager_id": "99",
        "order_id": "202",
        "customer_id": "7"
    }

    response = client.post("/notify-new-order", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["user_id"] == "99"
    assert response.json()["notification"]["type"] == "manager_new_order_alert"
    assert response.json()["notification"]["order_id"] == "202"


def test_get_user_notifications():
    client.post("/notify-new-order", json={
        "manager_id": "99",
        "order_id": "202",
        "customer_id": "7"
    })

    response = client.get("/users/99/notifications")

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_mark_notification_as_read():
    client.post("/notify-new-order", json={
        "manager_id": "99",
        "order_id": "202",
        "customer_id": "7"
    })

    response = client.patch("/notifications/1/read")

    assert response.status_code == 200
    assert response.json()["status"] == "notification marked as read"
    assert response.json()["notification"]["is_read"] is True


def test_get_default_preferences():
    response = client.get("/users/1/preferences")

    assert response.status_code == 200
    assert response.json()["user_id"] == "1"
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
        "user_id": "1",
        "order_id": "101",
        "old_status": "Preparing",
        "new_status": "Delivered"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "notification blocked by user preferences"


def test_status_notification_sent_when_enabled():
    response = client.post("/notify-status-change", json={
        "user_id": "1",
        "order_id": "101",
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
        "user_id": "1",
        "title": "Promo",
        "message": "You got 10 percent off",
        "type": "promo_update"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "notification blocked by user preferences"


def test_notify_order_event_placed():
    response = client.post("/notify-order-event", json={
        "user_id": "1",
        "order_id": "500",
        "event": "placed"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["title"] == "Order Placed"
    assert response.json()["notification"]["order_id"] == "500"


def test_notify_order_event_out_for_delivery():
    response = client.post("/notify-order-event", json={
        "user_id": "1",
        "order_id": "500",
        "event": "out_for_delivery"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "notification sent"
    assert response.json()["notification"]["title"] == "Out for Delivery"
    assert response.json()["notification"]["type"] == "order_status_update"


def test_notify_order_event_blocked_by_preferences():
    client.put("/users/1/preferences", json={
        "order_status_updates": False
    })

    response = client.post("/notify-order-event", json={
        "user_id": "1",
        "order_id": "500",
        "event": "confirmed"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "notification blocked by user preferences"