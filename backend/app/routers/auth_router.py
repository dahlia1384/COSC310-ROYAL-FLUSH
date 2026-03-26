from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from app.services.auth_dependencies import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session) -> AuthService:
    user_repository = UserRepository(db)
    session_repository = SessionRepository(db)
    return AuthService(user_repository, session_repository)


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = get_auth_service(db)

    try:
        user = auth_service.register(
            email=request.email,
            password=request.password,
            role=request.role,
        )
        return {
            "message": "Account created successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = get_auth_service(db)

    try:
        return auth_service.login(
            email=request.email,
            password=request.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
def logout(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    auth_service = get_auth_service(db)

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]

    try:
        return auth_service.logout(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }

@router.get("/owner-only")
def owner_only(current_user=Depends(require_role("RESTAURANT_OWNER"))):
    return {
        "message": "Welcome, restaurant owner",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
        },
    }