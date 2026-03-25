import csv
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.payment import PaymentAttempt
from app.repositories.payment_repository import (
    create_payment_attempt,
    count_attempts_by_order_id,
    get_attempts_by_order_id,
)

ALLOWED_PAYMENT_METHODS = {"credit_card", "debit_card", "paypal"}

CSV_FILE_PATH = Path(__file__).resolve().parents[1] / "data" / "food_delivery.csv"

def get_order_from_csv(order_id: str):
    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("order_id") == order_id:
                return row
    return None

def process_payment(db: Session, order_id: str, current_customer_id: str, payment_data):
    order = get_order_from_csv(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.get("customer_id") != current_customer_id:
        raise HTTPException(status_code=403, detail="You are not allowed to pay for this order")

    if payment_data.payment_method not in ALLOWED_PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    existing_attempts = get_attempts_by_order_id(db, order_id)
    if any(attempt.status == "success" for attempt in existing_attempts):
        raise HTTPException(status_code=400, detail="Order is already paid")

    attempt_number = count_attempts_by_order_id(db, order_id) + 1

    amount = float(order["order_value"])
    is_success = payment_data.simulate_success
    failure_reason = None if is_success else "Simulated payment failure"

    payment_attempt = PaymentAttempt(
        order_id=order["order_id"],
        customer_id=order["customer_id"],
        amount=amount,
        payment_method=payment_data.payment_method,
        status="success" if is_success else "failed",
        attempt_number=attempt_number,
        failure_reason=failure_reason,
    )

    create_payment_attempt(db, payment_attempt)

    return {
        "message": "Payment successful" if is_success else "Payment failed. Please retry.",
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "order_status": "paid" if is_success else "pending",
        "payment_status": "success" if is_success else "failed",
        "attempt_number": attempt_number,
        "failure_reason": failure_reason,
    }


def get_payment_attempt_history(db: Session, order_id: str, current_customer_id: str):
    order = get_order_from_csv(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.get("customer_id") != current_customer_id:
        raise HTTPException(status_code=403, detail="You are not allowed to view this order")

    return get_attempts_by_order_id(db, order_id)
