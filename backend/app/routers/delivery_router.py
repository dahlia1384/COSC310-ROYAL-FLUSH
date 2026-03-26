from fastapi import APIRouter, status
from app.schemas.delivery_schema import Delivery, DeliveryStatusUpdate
from app.services.delivery_services import(
    get_delivery,
    change_delivery_status,
)

router = APIRouter (prefix = "/deliveries", tags = ["deliveries"])

@router.get("/{order_id}", response_model = Delivery)
def get_delivery_order(order_id: str):
    return get_delivery(order_id)

@router.put("/{order_id}/status", response_model = Delivery)
def update_delivery_status(order_id: str, payload: DeliveryStatusUpdate):
    return change_delivery_status(order_id, payload.delivery_status)