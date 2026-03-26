from sqlalchemy.orm import Session
from app.models.payment import PaymentAttempt


def create_payment_attempt(db: Session, payment_attempt: PaymentAttempt) -> PaymentAttempt:
    db.add(payment_attempt)
    db.commit()
    db.refresh(payment_attempt)
    return payment_attempt


def count_attempts_by_order_id(db: Session, order_id: str) -> int:
    return (
        db.query(PaymentAttempt)
        .filter(PaymentAttempt.order_id == order_id)
        .count()
    )


def get_attempts_by_order_id(db: Session, order_id: str) -> list[PaymentAttempt]:
    return (
        db.query(PaymentAttempt)
        .filter(PaymentAttempt.order_id == order_id)
        .order_by(PaymentAttempt.attempt_number.asc())
        .all()
    )