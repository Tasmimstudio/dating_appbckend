# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class UserPreferences(BaseModel):
    min_age: int = Field(ge=18, le=100)
    max_age: int = Field(ge=18, le=100)
    max_distance: int = Field(ge=1, le=500)  # in kilometers
    gender_preference: List[GenderEnum]

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int = Field(ge=18, le=100)
    gender: GenderEnum
    bio: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    height: Optional[int] = None  # in cm
    occupation: Optional[str] = None
    education: Optional[str] = None
    interests: Optional[List[str]] = None
    preferences: Optional[UserPreferences] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    height: Optional[int] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    interests: Optional[List[str]] = None
    preferences: Optional[UserPreferences] = None

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    age: int
    gender: GenderEnum
    bio: Optional[str] = None
    city: Optional[str] = None
    height: Optional[int] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    interests: Optional[List[str]] = None
    preferences: Optional[UserPreferences] = None
    is_verified: bool = False
    created_at: Optional[str] = None
    last_active: Optional[str] = None

class UserProfile(BaseModel):
    """Public profile view for other users"""
    user_id: str
    name: str
    age: int
    gender: GenderEnum
    bio: Optional[str] = None
    city: Optional[str] = None
    height: Optional[int] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    distance: Optional[float] = None  # calculated distance from current user
