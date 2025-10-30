# app/schemas/swipe.py
from pydantic import BaseModel
from enum import Enum

class SwipeActionEnum(str, Enum):
    like = "like"
    dislike = "dislike"
    super_like = "super_like"

class SwipeCreate(BaseModel):
    from_user_id: str
    to_user_id: str
    action: SwipeActionEnum

class SwipeResponse(BaseModel):
    swipe_id: str
    from_user_id: str
    to_user_id: str
    action: SwipeActionEnum
    timestamp: str
    is_match: bool = False  # True if both users liked each other
