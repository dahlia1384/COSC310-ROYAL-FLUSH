from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, UTC

app = FastAPI(title="Notification Service")


class GeneralNotificationRequest(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    type: str = Field(default="general", min_length=1)


class StatusChangeNotificationRequest(BaseModel):
    user_id: int
    order_id: int
    old_status: str = Field(..., min_length=1)
    new_status: str = Field(..., min_length=1)


class ManagerAlertRequest(BaseModel):
    manager_id: int
    order_id: int
    customer_id: int
    message: Optional[str] = None


class NotificationPreference(BaseModel):
    user_id: int
    order_status_updates: bool = True
    promotions: bool = True
    general_notifications: bool = True


class NotificationPreferenceUpdate(BaseModel):
    order_status_updates: Optional[bool] = None
    promotions: Optional[bool] = None
    general_notifications: Optional[bool] = None


class Notification(BaseModel):
    notification_id: int
    user_id: int
    title: str
    message: str
    type: str
    order_id: Optional[int] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    is_read: bool
    created_at: str


notifications_db: List[Notification] = []
preferences_db: dict[int, NotificationPreference] = {}
next_notification_id = 1


def get_or_create_preferences(user_id: int) -> NotificationPreference:
    if user_id not in preferences_db:
        preferences_db[user_id] = NotificationPreference(user_id=user_id)
    return preferences_db[user_id]


def notification_allowed(user_id: int, notification_type: str) -> bool:
    prefs = get_or_create_preferences(user_id)

    if notification_type == "order_status_update":
        return prefs.order_status_updates
    if notification_type == "promo_update":
        return prefs.promotions
    if notification_type == "general":
        return prefs.general_notifications

    return True


def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    order_id: Optional[int] = None,
    old_status: Optional[str] = None,
    new_status: Optional[str] = None
):
    global next_notification_id

    notification = Notification(
        notification_id=next_notification_id,
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        order_id=order_id,
        old_status=old_status,
        new_status=new_status,
        is_read=False,
        created_at=datetime.now(UTC).isoformat()
    )

    notifications_db.append(notification)
    next_notification_id += 1
    return notification


@app.get("/")
def root():
    return {"message": "Notification service running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/users/{user_id}/preferences")
def get_user_preferences(user_id: int):
    return get_or_create_preferences(user_id).model_dump()


@app.put("/users/{user_id}/preferences")
def update_user_preferences(user_id: int, data: NotificationPreferenceUpdate):
    prefs = get_or_create_preferences(user_id)

    if data.order_status_updates is not None:
        prefs.order_status_updates = data.order_status_updates
    if data.promotions is not None:
        prefs.promotions = data.promotions
    if data.general_notifications is not None:
        prefs.general_notifications = data.general_notifications

    preferences_db[user_id] = prefs
    return {
        "status": "preferences updated",
        "preferences": prefs.model_dump()
    }


@app.post("/send-general")
def send_general_notification(data: GeneralNotificationRequest):
    if not notification_allowed(data.user_id, data.type):
        return {
            "status": "notification blocked by user preferences",
            "user_id": data.user_id,
            "type": data.type
        }

    notification = create_notification(
        user_id=data.user_id,
        title=data.title,
        message=data.message,
        notification_type=data.type
    )

    return {
        "status": "notification sent",
        "notification": notification.model_dump()
    }


@app.post("/notify-status-change")
def notify_status_change(data: StatusChangeNotificationRequest):
    if not notification_allowed(data.user_id, "order_status_update"):
        return {
            "status": "notification blocked by user preferences",
            "user_id": data.user_id,
            "type": "order_status_update"
        }

    notification = create_notification(
        user_id=data.user_id,
        title="Order Status Updated",
        message=f"Your order #{data.order_id} status changed from {data.old_status} to {data.new_status}.",
        notification_type="order_status_update",
        order_id=data.order_id,
        old_status=data.old_status,
        new_status=data.new_status
    )

    return {
        "status": "notification sent",
        "notification": notification.model_dump()
    }


@app.post("/notify-new-order")
def notify_new_order(data: ManagerAlertRequest):
    message = data.message or f"New order #{data.order_id} was placed by customer #{data.customer_id}."

    notification = create_notification(
        user_id=data.manager_id,
        title="New Order Alert",
        message=message,
        notification_type="manager_new_order_alert",
        order_id=data.order_id
    )

    return {
        "status": "notification sent",
        "notification": notification.model_dump()
    }


@app.get("/users/{user_id}/notifications")
def get_user_notifications(user_id: int):
    user_notifications = [
        notification.model_dump()
        for notification in notifications_db
        if notification.user_id == user_id
    ]

    return {
        "user_id": user_id,
        "count": len(user_notifications),
        "notifications": user_notifications
    }


@app.get("/users/{user_id}/notifications/unread")
def get_unread_notifications(user_id: int):
    unread_notifications = [
        notification.model_dump()
        for notification in notifications_db
        if notification.user_id == user_id and not notification.is_read
    ]

    return {
        "user_id": user_id,
        "count": len(unread_notifications),
        "notifications": unread_notifications
    }


@app.patch("/notifications/{notification_id}/read")
def mark_notification_as_read(notification_id: int):
    for notification in notifications_db:
        if notification.notification_id == notification_id:
            notification.is_read = True
            return {
                "status": "notification marked as read",
                "notification": notification.model_dump()
            }

    raise HTTPException(status_code=404, detail="Notification not found")