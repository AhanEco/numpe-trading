"""Authentication and token verification for administrative access."""

from __future__ import annotations

import datetime
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hash or plain configured admin password."""
    if plain_password == settings.ADMIN_PASSWORD:
        return True
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Create signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_admin(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    """Dependency that ensures the caller is an authenticated administrator."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
        if role != "admin":
            raise credentials_exception
        return payload
    except Exception:
        raise credentials_exception

