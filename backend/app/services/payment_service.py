import httpx
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.payment import PaymentAttempt
from app.models.user import User
from app.repositories.payment_repository import (
    create_payment_attempt,
    count_attempts_by_order_id,
    get_attempts_by_order_id,
)
from app.repositories.orders_repo import get_order_by_id, update_order_status, update_order_total
from app.services.delivery_services import create_new_delivery

ALLOWED_PAYMENT_METHODS = {"credit_card", "debit_card", "paypal", "wallet"}
PRICE_SERVICE = os.getenv("PRICE_URL", "http://price_service:8002")
NOTIFICATION_SERVICE = os.getenv("NOTIFICATION_URL", "http://notification_service:8001")


def _calculate_total(order: dict, promo_code: str = None) -> float:
    try:
        response = httpx.post(
            f"{PRICE_SERVICE}/calculate",
            json={
                "user_id": order["customer_id"],
                "items": order["items"],
                "promo_code": promo_code,
            },
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()["total"]
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Price service unavailable")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Price service timed out")
    except (KeyError, ValueError):
        raise HTTPException(status_code=502, detail="Invalid response from price service")


def _send_payment_notification(customer_id: str, order_id: str, amount: float):
    try:
        with httpx.Client(timeout=3.0) as client:
            client.post(
                f"{NOTIFICATION_SERVICE}/send-general",
                json={
                    "user_id": customer_id,
                    "title": "Payment confirmed",
                    "message": f"Your payment of ${amount:.2f} for order {order_id} was successful.",
                    "type": "general",
                },
            )
    except Exception:
        pass

def _send_payment_notification_for_wallet_topup(customer_id: str, amount: float):
    try:
        with httpx.Client(timeout=3.0) as client:
            client.post(
                f"{NOTIFICATION_SERVICE}/send-general",
                json={
                    "user_id": customer_id,
                    "title": "Payment confirmed",
                    "message": f"Your top up of ${amount:.2f} was successful for the wallet.",
                    "type": "general",
                },
            )
    except Exception:
        pass


def process_payment(db: Session, order_id: str, customer_id: str, payment_data):
    order = get_order_by_id(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.get("customer_id") != customer_id:
        raise HTTPException(status_code=403, detail="You are not allowed to pay for this order")

    if order.get("order_status") != "Pending Payment":
        raise HTTPException(status_code=400, detail="Order is not awaiting payment")

    if payment_data.payment_method not in ALLOWED_PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    existing_attempts = get_attempts_by_order_id(db, order_id)
    if any(attempt.status == "success" for attempt in existing_attempts):
        raise HTTPException(status_code=400, detail="Order is already paid")
    
    user = db.query(User).filter(User.id == customer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    

    amount = _calculate_total(order, promo_code=payment_data.promo_code)
    print("PAYMENT DEBUG")
    print("order_id:", order_id)
    print("order items:", order.get("items"))
    print("calculated amount:", amount)
    print("wallet before:", user.wallet)

    if payment_data.payment_method == "wallet" and user.wallet < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in wallet")

    attempt_number = count_attempts_by_order_id(db, order_id) + 1
    is_success = payment_data.simulate_success
    failure_reason = None if is_success else "Simulated payment failure"

    payment_attempt = PaymentAttempt(
        order_id=order_id,
        customer_id=customer_id,
        amount=amount,
        payment_method=payment_data.payment_method,
        status="success" if is_success else "failed",
        attempt_number=attempt_number,
        failure_reason=failure_reason,
    )
    create_payment_attempt(db, payment_attempt)

    if is_success:
        if payment_data.payment_method == "wallet":
            user.wallet = round(user.wallet - amount, 2)
            db.commit()
            db.refresh(user)
        update_order_status(order_id, "Paid")
        update_order_total(order_id, amount)
        create_new_delivery(order)
        _send_payment_notification(customer_id, order_id, amount)

    return {
        "message": "Payment successful" if is_success else "Payment failed. Please retry.",
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "order_status": "Paid" if is_success else "Pending Payment",
        "payment_status": "success" if is_success else "failed",
        "attempt_number": attempt_number,
        "failure_reason": failure_reason,
    }


def get_payment_attempt_history(db: Session, order_id: str, customer_id: str):
    order = get_order_by_id(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.get("customer_id") != customer_id:
        raise HTTPException(status_code=403, detail="You are not allowed to view this order")

    return get_attempts_by_order_id(db, order_id)


def process_payment_for_wallet(db: Session, customer_id: str, payment_data):
    if payment_data.payment_method not in ALLOWED_PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    if payment_data.payment_method == "wallet":
        raise HTTPException(status_code=400, detail="Wallet cannot be used to top up wallet")

    user = db.query(User).filter(User.id == customer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.wallet = round(user.wallet + payment_data.amount, 2)
    db.commit()
    db.refresh(user)
    _send_payment_notification_for_wallet_topup(customer_id, payment_data.amount)

    return {
        "message": "Payment successful",
        "customer_id": customer_id,
        "amount": payment_data.amount,
        "new_wallet_balance": user.wallet,
    }
