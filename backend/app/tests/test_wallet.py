import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_EMAIL = f"wallet_test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "SecurePass123!"


@pytest.fixture(scope="module")
def registered_user():
    """Register a fresh user and return their id, email, and password."""
    resp = client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "role": "CUSTOMER"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["user"]


def test_get_wallet_balance(registered_user):
    """POST /wallet returns the wallet balance for valid credentials."""
    resp = client.post(
        "/wallet",
        params={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "wallet" in data
    assert data["wallet"] == 0.0


def test_wallet_topup_increases_balance(registered_user):
    """PUT /wallet/topup adds the requested amount to the user's wallet."""
    customer_id = registered_user["id"]

    resp = client.put(
        "/wallet/topup",
        params={"customer_id": customer_id},
        json={"amount": 50.0, "payment_method": "credit_card"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Payment successful"
    assert data["customer_id"] == customer_id
    assert data["amount"] == 50.0
    assert data["new_wallet_balance"] == 50.0

    balance_resp = client.post(
        "/wallet",
        params={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert balance_resp.json()["wallet"] == 50.0


def test_wallet_topup_rejects_wallet_as_payment_method(registered_user):
    """PUT /wallet/topup returns 400 when payment_method is 'wallet'."""
    customer_id = registered_user["id"]

    resp = client.put(
        "/wallet/topup",
        params={"customer_id": customer_id},
        json={"amount": 20.0, "payment_method": "wallet"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Wallet cannot be used to top up wallet"