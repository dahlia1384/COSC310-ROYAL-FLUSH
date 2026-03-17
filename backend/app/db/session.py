from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite connection URL (file-based)

DATABASE_URL = "sqlite:///./food_delivery.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)