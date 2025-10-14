# app/schemas/match.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchCreate(BaseModel):
    user1_id: str
    user2_id: str

class MatchResponse(BaseModel):
    match_id: str
    user1_id: str
    user2_id: str
    matched_at: str
    conversation_started: bool = False
    last_message_at: Optional[str] = None

class MatchWithProfile(BaseModel):
    """Match response with the other user's profile"""
    match_id: str
    matched_at: str
    conversation_started: bool
    last_message_at: Optional[str] = None
    matched_user: dict  # UserProfile from User schema
