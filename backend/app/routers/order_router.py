from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from typing import List
from app.schemas.order_schema import Order, OrderCreate, OrderStatusUpdate
from app.schemas.payment import PaymentResponse, PaymentRequest
from app.services.order_services import(
    create_new_order,
    get_order,
    list_customer_orders,
    change_order_status,
)
from app.services.payment_service import (
    process_payment
)

router = APIRouter (prefix = "/orders", tags = ["orders"])

@router.post("", response_model = Order, status_code = status.HTTP_201_CREATED)
def post_order(payload: OrderCreate):
    return create_new_order(payload)

@router.get("/customer/{customer_id}", response_model = List[Order])
def get_orders_by_customer(customer_id:str):
    return list_customer_orders(customer_id)

@router.get("/{order_id}", response_model = Order)
def get_single_order(order_id: str):
    return get_order(order_id)

@router.put("/{order_id}/status", response_model = Order)
def get_order_status(order_id: str, payload: OrderStatusUpdate):
    return change_order_status(order_id, payload.order_status)

@router.post("/{order_id}/pay", response_model=PaymentResponse)
def pay_for_order(order_id: str, payload: PaymentRequest, db: Session = Depends(get_db)):
    return process_payment(db, order_id, payload.customer_id, payload)
