# app/routes/interest.py
from fastapi import APIRouter, HTTPException
from app import crud
from app.schemas.Interest import InterestCreate, InterestResponse, UserInterestCreate, UserInterestsResponse
from typing import List

router = APIRouter(prefix="/interests", tags=["Interests"])

@router.post("/", response_model=InterestResponse)
def create_interest(interest: InterestCreate):
    """Create a new interest"""
    new_interest = crud.interest.create_interest(interest.name, interest.category)
    return new_interest.__dict__

@router.get("/", response_model=List[InterestResponse])
def get_all_interests(category: str = None):
    """Get all interests, optionally filtered by category"""
    interests = crud.interest.get_all_interests(category)
    return [i.__dict__ for i in interests]

@router.get("/{interest_id}", response_model=InterestResponse)
def get_interest(interest_id: str):
    interest = crud.interest.get_interest_by_id(interest_id)
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found")
    return interest.__dict__

@router.post("/user", response_model=InterestResponse)
def add_user_interest(user_interest: UserInterestCreate):
    """Add an interest to a user's profile"""
    # Verify user exists
    user = crud.user.get_user_by_id(user_interest.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify interest exists
    interest = crud.interest.get_interest_by_id(user_interest.interest_id)
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found")

    result = crud.interest.add_user_interest(user_interest.user_id, user_interest.interest_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to add interest")

    return result.__dict__

@router.delete("/user/{user_id}/{interest_id}")
def remove_user_interest(user_id: str, interest_id: str):
    """Remove an interest from a user's profile"""
    crud.interest.remove_user_interest(user_id, interest_id)
    return {"message": "Interest removed successfully"}

@router.get("/user/{user_id}")
def get_user_interests(user_id: str):
    """Get all interests for a user"""
    interests = crud.interest.get_user_interests(user_id)
    return {
        "user_id": user_id,
        "interests": [i.__dict__ for i in interests]
    }

@router.get("/common/{user1_id}/{user2_id}", response_model=List[InterestResponse])
def get_common_interests(user1_id: str, user2_id: str):
    """Get common interests between two users"""
    interests = crud.interest.get_common_interests(user1_id, user2_id)
    return [i.__dict__ for i in interests]
