"""
JWT Authentication Utilities
Handles token creation, validation, and user identification
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
_DEFAULT_SECRET_KEY = "your-secret-key-change-this"
SECRET_KEY = os.getenv("SECRET_KEY", _DEFAULT_SECRET_KEY)
if SECRET_KEY == _DEFAULT_SECRET_KEY:
    logger.warning("SECRET_KEY is using the default placeholder value. Set a strong SECRET_KEY in production.")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security scheme
security = HTTPBearer()


class TokenData:
    """Token payload data"""

    def __init__(self, user_id: int, email: str):
        self.user_id = user_id
        self.email = email


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash"""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = {"user_id": user_id, "email": email}

    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str) -> TokenData:
    """Verify and decode a JWT access token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id, email=email)
    except JWTError:
        raise credentials_exception

    return token_data


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Dependency to get current user from JWT token"""
    token = credentials.credentials
    return verify_access_token(token)
