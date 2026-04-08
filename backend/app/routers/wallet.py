from fastapi import APIRouter, HTTPException

from fastapi.params import Depends
from pytest import Session
from app.db.deps import get_db
from app.models.user import User
from app.services.security import verify_password
from app.services.payment_service import process_payment_for_wallet
from app.schemas.payment import WalletPaymentData

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.post("")
def get_wallet(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """ Get wallet balance for a user by email and password. """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"wallet": user.wallet}

@router.put("/topup")
def put_wallet(
    customer_id: str,
    payment_data: WalletPaymentData,
    db: Session = Depends(get_db)
):
    """ Update wallet balance for a user by email and password. """
    return process_payment_for_wallet(db, customer_id, payment_data)