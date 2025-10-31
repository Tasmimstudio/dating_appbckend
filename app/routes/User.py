# app/routes/user.py
from fastapi import APIRouter, HTTPException
from app.crud import user as crud_user
from app.crud import Photo as crud_photo
from app.schemas.User import UserCreate, UserResponse, UserUpdate
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

class InterestsUpdate(BaseModel):
    interests: List[str]

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    new_user = crud_user.create_user(user)
    return new_user.__dict__

@router.get("/search/by-name", response_model=List[UserResponse])
def search_users(query: str, current_user_id: str = None, limit: int = 20):
    """Search users by name or email"""
    if not query or len(query) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    users = crud_user.search_users(query, limit, current_user_id)
    return [user.__dict__ for user in users]

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch user photos
    photos = crud_photo.get_user_photos(user_id)
    photos_list = [p.__dict__ for p in photos] if photos else []

    # Add photos to user dict
    user_dict = user.__dict__
    user_dict['photos'] = photos_list

    return user_dict

@router.get("/{user_id}/potential-matches")
def get_potential_matches(user_id: str):
    """Get users that this user can swipe on (excluding already swiped users)"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all users except self and already swiped users
    potential_matches = crud_user.get_potential_matches(user_id)
    return potential_matches

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_update: UserUpdate):
    """Update user profile"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = crud_user.update_user(user_id, user_update)
    return updated_user.__dict__

@router.put("/{user_id}/interests", response_model=UserResponse)
def update_user_interests(user_id: str, interests_data: InterestsUpdate):
    """Update user interests"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create UserUpdate with just interests
    user_update = UserUpdate(interests=interests_data.interests)
    updated_user = crud_user.update_user(user_id, user_update)
    return updated_user.__dict__
