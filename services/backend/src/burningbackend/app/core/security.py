from datetime import datetime, timedelta
from hashlib import md5
import secrets
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_api_key() -> str:
    return md5(secrets.token_bytes(32)).hexdigest()


def create_access_token(subject: str, expires_delta: timedelta, secret_key: str) -> str:
    expire = datetime.utcnow() + expires_delta
    return jwt.encode({"sub": subject, "exp": expire}, secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, secret_key: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
