from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, UTC

router = APIRouter(tags=["notifications"])


ORDER_EVENT_TO_TITLE = {
    "placed": "Order Placed",
    "confirmed": "Order Confirmed",
    "preparing": "Order Being Prepared",
    "out_for_delivery": "Out for Delivery",
    "delivered": "Order Delivered",
    "completed": "Order Completed",
    "cancelled": "Order Cancelled",
}


def build_order_event_message(order_id: str, event: str) -> str:
    messages = {
        "placed": f"Your order #{order_id} has been placed successfully.",
        "confirmed": f"Your order #{order_id} has been confirmed.",
        "preparing": f"Your order #{order_id} is now being prepared.",
        "out_for_delivery": f"Your order #{order_id} is now out for delivery.",
        "delivered": f"Your order #{order_id} has been delivered.",
        "completed": f"Your order #{order_id} has been completed.",
        "cancelled": f"Your order #{order_id} has been cancelled.",
    }
    return messages.get(event, f"Your order #{order_id} status was updated to {event}.")


class GeneralNotificationRequest(BaseModel):
    user_id: str
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    type: str = Field(default="general", min_length=1)


class StatusChangeNotificationRequest(BaseModel):
    user_id: str
    order_id: str
    old_status: str = Field(..., min_length=1)
    new_status: str = Field(..., min_length=1)


class OrderEventNotificationRequest(BaseModel):
    user_id: str
    order_id: str
    event: Literal[
        "placed",
        "confirmed",
        "preparing",
        "out_for_delivery",
        "delivered",
        "completed",
        "cancelled",
    ]


class ManagerAlertRequest(BaseModel):
    manager_id: str
    order_id: str
    customer_id: str
    message: Optional[str] = None


class NotificationPreference(BaseModel):
    user_id: str
    order_status_updates: bool = True
    promotions: bool = True
    general_notifications: bool = True


class NotificationPreferenceUpdate(BaseModel):
    order_status_updates: Optional[bool] = None
    promotions: Optional[bool] = None
    general_notifications: Optional[bool] = None


class Notification(BaseModel):
    notification_id: int
    user_id: str
    title: str
    message: str
    type: str
    order_id: Optional[str] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    is_read: bool
    created_at: str


notifications_db: List[Notification] = []
preferences_db: dict[str, NotificationPreference] = {}
next_notification_id = 1


def get_or_create_preferences(user_id: str) -> NotificationPreference:
    if user_id not in preferences_db:
        preferences_db[user_id] = NotificationPreference(user_id=user_id)
    return preferences_db[user_id]


def notification_allowed(user_id: str, notification_type: str) -> bool:
    prefs = get_or_create_preferences(user_id)

    if notification_type == "order_status_update":
        return prefs.order_status_updates
    if notification_type == "promo_update":
        return prefs.promotions
    if notification_type == "general":
        return prefs.general_notifications

    return True


def create_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str,
    order_id: Optional[str] = None,
    old_status: Optional[str] = None,
    new_status: Optional[str] = None,
) -> Notification:
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
        created_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )

    notifications_db.append(notification)
    next_notification_id += 1
    return notification


@router.get("/notifications")
def notification_root():
    return {"message": "Notification service running"}


@router.get("/users/{user_id}/preferences")
def get_user_preferences(user_id: str):
    return get_or_create_preferences(user_id).model_dump()


@router.put("/users/{user_id}/preferences")
def update_user_preferences(user_id: str, data: NotificationPreferenceUpdate):
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
        "preferences": prefs.model_dump(),
    }


@router.post("/send-general")
def send_general_notification(data: GeneralNotificationRequest):
    if not notification_allowed(data.user_id, data.type):
        return {
            "status": "notification blocked by user preferences",
            "user_id": data.user_id,
            "type": data.type,
        }

    notification = create_notification(
        user_id=data.user_id,
        title=data.title,
        message=data.message,
        notification_type=data.type,
    )

    return {
        "status": "notification sent",
        "notification": notification.model_dump(),
    }


@router.post("/notify-status-change")
def notify_status_change(data: StatusChangeNotificationRequest):
    if not notification_allowed(data.user_id, "order_status_update"):
        return {
            "status": "notification blocked by user preferences",
            "user_id": data.user_id,
            "type": "order_status_update",
        }

    notification = create_notification(
        user_id=data.user_id,
        title="Order Status Updated",
        message=f"Your order #{data.order_id} status changed from {data.old_status} to {data.new_status}.",
        notification_type="order_status_update",
        order_id=data.order_id,
        old_status=data.old_status,
        new_status=data.new_status,
    )

    return {
        "status": "notification sent",
        "notification": notification.model_dump(),
    }


@router.post("/notify-order-event")
def notify_order_event(data: OrderEventNotificationRequest):
    if not notification_allowed(data.user_id, "order_status_update"):
        return {
            "status": "notification blocked by user preferences",
            "user_id": data.user_id,
            "type": "order_status_update",
        }

    notification = create_notification(
        user_id=data.user_id,
        title=ORDER_EVENT_TO_TITLE[data.event],
        message=build_order_event_message(data.order_id, data.event),
        notification_type="order_status_update",
        order_id=data.order_id,
        new_status=data.event,
    )

    return {
        "status": "notification sent",
        "notification": notification.model_dump(),
    }


@router.post("/notify-new-order")
def notify_new_order(data: ManagerAlertRequest):
    message = data.message or f"New order #{data.order_id} was placed by customer #{data.customer_id}."

    notification = create_notification(
        user_id=data.manager_id,
        title="New Order Alert",
        message=message,
        notification_type="manager_new_order_alert",
        order_id=data.order_id,
    )

    return {
        "status": "notification sent",
        "notification": notification.model_dump(),
    }


@router.get("/users/{user_id}/notifications")
def get_user_notifications(user_id: str):
    user_notifications = [
        notification.model_dump()
        for notification in notifications_db
        if notification.user_id == user_id
    ]

    return {
        "user_id": user_id,
        "count": len(user_notifications),
        "notifications": user_notifications,
    }


@router.get("/users/{user_id}/notifications/unread")
def get_unread_notifications(user_id: str):
    unread_notifications = [
        notification.model_dump()
        for notification in notifications_db
        if notification.user_id == user_id and not notification.is_read
    ]

    return {
        "user_id": user_id,
        "count": len(unread_notifications),
        "notifications": unread_notifications,
    }


@router.patch("/notifications/{notification_id}/read")
def mark_notification_as_read(notification_id: int):
    for notification in notifications_db:
        if notification.notification_id == notification_id:
            notification.is_read = True
            return {
                "status": "notification marked as read",
                "notification": notification.model_dump(),
            }
    raise HTTPException(status_code=404, detail="Notification not found")