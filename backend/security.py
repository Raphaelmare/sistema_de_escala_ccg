from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def normalize_password(password: str | None) -> str:
    if password is None:
        return ""
    password = str(password)
    return password.strip()[:72]


def hash_password(password: str | None) -> str:
    normalized = normalize_password(password)
    if not normalized:
        raise ValueError("A senha não pode estar vazia.")
    return pwd_context.hash(normalized)


def verify_password(plain_password: str | None, hashed_password: str | None) -> bool:
    if not plain_password or not hashed_password:
        return False
    normalized_plain = normalize_password(plain_password)
    try:
        return pwd_context.verify(normalized_plain, hashed_password)
    except Exception:
        return normalized_plain == hashed_password


def create_access_token(subject: str, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if not isinstance(payload, dict):
            raise ValueError("Token inválido.")
        return payload
    except (JWTError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.") from exc
