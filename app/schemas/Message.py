# app/schemas/message.py
from pydantic import BaseModel
from typing import Optional

class MessageCreate(BaseModel):
    sender_id: str
    receiver_id: str
    content: str
    match_id: Optional[str] = None

class MessageUpdate(BaseModel):
    read: bool = True

class MessageResponse(BaseModel):
    message_id: str
    sender_id: str
    receiver_id: str
    content: str
    sent_at: str
    match_id: Optional[str] = None
    read_at: Optional[str] = None
    is_read: bool = False

class ConversationResponse(BaseModel):
    """All messages in a conversation"""
    match_id: str
    messages: list[MessageResponse]
    total_count: int
