"""
Authentication Routes
User signup, login, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, User as UserSchema, LoginRequest, TokenResponse
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    TokenData,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=UserSchema)
async def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account

    - **email**: User email (must be unique)
    - **username**: Username (must be unique)
    - **password**: Password (will be hashed)
    """
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_create.email) | (User.username == user_create.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    # Create user
    hashed_password = hash_password(user_create.password)
    db_user = User(
        email=user_create.email,
        username=user_create.username,
        password_hash=hashed_password,
        is_active=True,
        balance=0.0,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login and get JWT token

    - **email**: User email
    - **password**: User password

    Returns access token valid for 30 minutes
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Create token
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
    }


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user information"""
    user = db.query(User).filter(User.id == current_user.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
