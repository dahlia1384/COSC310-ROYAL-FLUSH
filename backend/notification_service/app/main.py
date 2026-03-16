from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

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
next_notification_id = 1


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
        created_at=datetime.utcnow().isoformat() + "Z"
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


@app.post("/send-general")
def send_general_notification(data: GeneralNotificationRequest):
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
    title = "Order Status Updated"
    message = f"Your order #{data.order_id} status changed from {data.old_status} to {data.new_status}."

    notification = create_notification(
        user_id=data.user_id,
        title=title,
        message=message,
        notification_type="order_status_update",
        order_id=data.order_id,
        old_status=data.old_status,
        new_status=data.new_status
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