from fastapi import HTTPException
from app.schemas.delivery_schema import Delivery
from app.repositories.delivery_repo import(
    create_delivery,
    get_delivery_by_order_id,
    update_delivery_status
    )

def create_new_delivery(order_data: dict) -> Delivery:
    method = order_data.get("delivery_method", "Unknown").capitalize()

    delivery data = {
        "order_id": order_data["order_id"],
        "restaurant_id: order_data["restaurant_id"],
        "delivery_status": "Preparing Order",
        "delivery_method": method,
        "delivery_time": datetime.utcnow().isoformat() }

    created = create_delivery(delivery_data)
    return Delivery(**created)

def get_delivery(order_id: str) -> Delivery:
    delivery = get_delivery_by_id(order_id)
    if not delivery:
        raise HTTPException(status_code = 404, detail = "Delivery Not Found")
    return Delivery(**delivery)

def change_delivery_status(order_id: str, status: str) -> Delivery:
    delivery = get_delivery_by_order_id(order_id)
    if not delivery:
        raise HTTPException(status_code = 404, detail = "Delivery Not Found") 
    
    if delivery.get("delivery_status") == "Order Delivered":
        raise HTTPException(status_code = 400, detail= "Can't modify completed delivery")

    updated = update_delivery_status(order_id, status)
    return Delivery(**updated)
