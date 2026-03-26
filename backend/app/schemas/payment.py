from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentRequest(BaseModel):
    customer_id: str
    payment_method: str
    simulate_success: bool
    promo_code: Optional[str] = None


class PaymentResponse(BaseModel):
    message: str
    order_id: str
    customer_id: str
    order_status: str
    payment_status: str
    attempt_number: int
    failure_reason: Optional[str] = None


class PaymentAttemptResponse(BaseModel):
    id: int
    order_id: str
    customer_id: str
    amount: float
    payment_method: str
    status: str
    attempt_number: int
    failure_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True