from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.security import decode_access_token


def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    token_id = payload.get("jti")
    user_id = payload.get("sub")

    if not token_id or not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    session_repository = SessionRepository(db)
    user_repository = UserRepository(db)

    session = session_repository.get_by_token_id(token_id)
    if not session or session.is_revoked:
        raise HTTPException(status_code=401, detail="Session is invalid or revoked")

    user = user_repository.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


def require_role(*allowed_roles: str):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    return role_checker