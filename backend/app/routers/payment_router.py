from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.payment import PaymentRequest, PaymentResponse, PaymentAttemptResponse
from app.services.auth_dependencies import get_current_user
from app.services.payment_service import process_payment, get_payment_attempt_history

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/orders/{order_id}", response_model=PaymentResponse)
def pay_for_order(
    order_id: str,
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return process_payment(db, order_id, str(current_user.id), payment_data)


@router.get("/orders/{order_id}/attempts", response_model=list[PaymentAttemptResponse])
def get_order_payment_attempts(
    order_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_payment_attempt_history(db, order_id, str(current_user.id))