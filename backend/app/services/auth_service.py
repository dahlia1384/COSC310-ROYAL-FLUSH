from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.services.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: SessionRepository,
    ) -> None:
        self.user_repository = user_repository
        self.session_repository = session_repository

    def register(self, email: str, password: str, role: str):
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("Email is already registered")

        if role not in ["CUSTOMER", "RESTAURANT_OWNER"]:
            raise ValueError("Invalid role")

        password_hash = hash_password(password)

        user = self.user_repository.create_user(
            email=email,
            password_hash=password_hash,
            role=role,
        )
        return user

    def login(self, email: str, password: str):
        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        if not user.is_active:
            raise ValueError("User account is inactive")

        access_token, token_id, expires_at = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )

        self.session_repository.create_session(
            user_id=user.id,
            token_id=token_id,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            },
        }

    def logout(self, token: str):
        payload = decode_access_token(token)
        token_id = payload.get("jti")

        if not token_id:
            raise ValueError("Invalid token")

        session = self.session_repository.revoke_session(token_id)
        if not session:
            raise ValueError("Session not found")

        return {"message": "Logged out successfully"}