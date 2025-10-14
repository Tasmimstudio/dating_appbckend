# app/routes/Auth.py
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.crud import user as crud_user
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas.User import UserCreate

# ✅ Removed prefix from router
router = APIRouter(tags=["Authentication"])

# ---------- Response Models ----------
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class LoginRequest(BaseModel):
    email: str
    password: str

# ---------- Register ----------
@router.post("/register", response_model=Token)
def register(user: UserCreate):
    """Register a new user and return access token"""
    existing_user = crud_user.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)

    user_dict = user.model_dump() if hasattr(user, 'model_dump') else user.dict()
    user_dict['password_hash'] = hashed_password
    new_user = crud_user.create_user_with_password(user_dict)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.user_id},
        expires_delta=access_token_expires
    )

    user_dict = new_user.__dict__.copy()
    user_dict.pop("password_hash", None)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

# ---------- Login ----------
@router.post("/login", response_model=Token)
def login(credentials: LoginRequest):
    """Login user and return access token"""
    user = crud_user.get_user_by_email(credentials.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires
    )

    user_dict = user.__dict__.copy()
    user_dict.pop("password_hash", None)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }
