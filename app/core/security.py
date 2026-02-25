from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from jose import jwt
from passlib.context import CryptContext

from app.core.config import config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: Optional[timedelta],
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    return _create_token(subject=subject, token_type="access", expires_delta=expires_delta)


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(days=7)
    return _create_token(subject=subject, token_type="refresh", expires_delta=expires_delta)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])


def create_token_pair(user_id: str) -> Tuple[str, str]:
    access_token = create_access_token(subject=user_id)
    refresh_token = create_refresh_token(subject=user_id)
    return access_token, refresh_token

