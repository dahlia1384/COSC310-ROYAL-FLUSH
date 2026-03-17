from typing import Optional

from sqlalchemy.orm import Session

from app.models.user_session import UserSession


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(
        self,
        user_id: str,
        token_id: str,
        expires_at,
    ) -> UserSession:
        session = UserSession(
            user_id=user_id,
            token_id=token_id,
            is_revoked=False,
            expires_at=expires_at,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_token_id(self, token_id: str) -> Optional[UserSession]:
        return (
            self.db.query(UserSession)
            .filter(UserSession.token_id == token_id)
            .first()
        )

    def revoke_session(self, token_id: str) -> Optional[UserSession]:
        session = self.get_by_token_id(token_id)
        if session:
            session.is_revoked = True
            self.db.commit()
            self.db.refresh(session)
        return session