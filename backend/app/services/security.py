from datetime import datetime, timedelta, UTC
import uuid

from passlib.context import CryptContext
import jwt


# security logic for feat 1
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "food-delivery-auth-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token generation
def create_access_token(user_id: str, email: str, role: str) -> tuple[str, str, datetime]:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_id = str(uuid.uuid4())

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "jti": token_id,
        "exp": expire,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, token_id, expire

# JWT decoding
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
