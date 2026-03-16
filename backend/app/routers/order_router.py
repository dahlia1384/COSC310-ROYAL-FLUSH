from fastapi import APIRouter, status
from typing import List
from app.schemas.order_schema import Order, OrderCreate, OrderStatusUpdate
from app.services.order_services import(
    create_new_order,
    get_order,
    list_customer_orders,
    change_order_status,
)

router = APIRouter (prefix = "/orders", tags = ["orders"])

@router.post("", response_model = Order, status_code = status.HTTP_201_CREATED)
def post_order(payload: OrderCreate):
    return create_new_order(payload)

@router.get("/{order_id}", response_model = Order)
def get_single_order(order_id: str):
    return get_order(order_id)

@router.get("/customer/{customer_id}", response_model = List[Order])
def get_orders_by_customer(customer_id:str):
    return list_customer_orders(customer_id)


@router.put("/{order_id}/status", response_model = Order)
def get_order_status(order_id: str, payload: OrderStatusUpdate):
    return change_order_status(order_id, payload.order_status)

