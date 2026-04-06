import pytest
from app.db.session import SessionLocal
from app.models.user import User
from app.services.security import hash_password

ORDER_TEST_CUSTOMER_ID = "ac8fc3f0-d128-4ffa-a5b1-6b803746a392"


@pytest.fixture(scope="session", autouse=True)
def seed_order_test_user():
    """Ensure the hardcoded customer used in order/payment tests exists in the DB."""
    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.id == ORDER_TEST_CUSTOMER_ID).first()
        if not exists:
            user = User(
                id=ORDER_TEST_CUSTOMER_ID,
                email="order_test_customer@example.com",
                password_hash=hash_password("testpassword"),
                role="CUSTOMER",
                wallet=1000.0,
            )
            db.add(user)
            db.commit()
    finally:
        db.close()