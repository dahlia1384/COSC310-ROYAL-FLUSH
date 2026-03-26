from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy knows about them
from app.models.user import User
from app.models.user_session import UserSession


def init_db() -> None:
    Base.metadata.create_all(bind=engine)