import uuid
from fastapi import HTTPException
from typing import List
from app.schemas.order_schema import Order, OrderCreate
from app.repositories.orders_repo import(
    create_order,
    get_order_by_id,
    get_orders_by_customer,
    update_order_status
    )

def create_new_order(payload: OrderCreate) -> Order:
    order_data = payload.dict()
    order_data["order_id"]= str (uuid.uuid4())
    order_data["order_status"] = "Order Created"
    created = create_order(order_data)
    return Order(**created)

def get_order(order_id: str) -> Order:
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code = 404, detail = "Order Not Found")
    return Order(**order)

def list_customer_orders(customer_id: str) -> List[Order]:
    orders = get_orders_by_customer(customer_id)
    return [Order (**o) for o in orders]

def change_order_status(order_id: str, status: str) -> Order:
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code = 404, detail = "Order Not Found") 
    
    if order.get("order_status") == "delivered":
        raise HTTPException(status_code = 400, detail= "Can't modify delivered order")

    updated = updated_order_status(order_id, status)
    return Order(**updated)








