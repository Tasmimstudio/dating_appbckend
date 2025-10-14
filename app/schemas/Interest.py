# app/schemas/interest.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class InterestCategoryEnum(str, Enum):
    sports = "sports"
    music = "music"
    food = "food"
    travel = "travel"
    art = "art"
    technology = "technology"
    fitness = "fitness"
    books = "books"
    movies = "movies"
    gaming = "gaming"
    outdoor = "outdoor"
    other = "other"

class InterestCreate(BaseModel):
    name: str
    category: InterestCategoryEnum

class InterestResponse(BaseModel):
    interest_id: str
    name: str
    category: InterestCategoryEnum

class UserInterestCreate(BaseModel):
    user_id: str
    interest_id: str

class UserInterestsResponse(BaseModel):
    """All interests for a user"""
    user_id: str
    interests: list[InterestResponse]
