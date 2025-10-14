# app/schemas/photo.py
from pydantic import BaseModel, HttpUrl
from typing import Optional

class PhotoCreate(BaseModel):
    user_id: str
    url: str  # URL to the uploaded photo
    is_primary: bool = False
    order: int = 0  # Display order (0 = first)

class PhotoUpdate(BaseModel):
    is_primary: Optional[bool] = None
    order: Optional[int] = None

class PhotoResponse(BaseModel):
    photo_id: str
    user_id: str
    url: str
    is_primary: bool
    order: int
    uploaded_at: str

class UserPhotosResponse(BaseModel):
    """All photos for a user"""
    user_id: str
    photos: list[PhotoResponse]
