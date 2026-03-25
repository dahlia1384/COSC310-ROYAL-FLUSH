from fastapi import APIRouter
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserCreate):
    return AuthService.register_user(user)
