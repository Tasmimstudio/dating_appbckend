# app/models/message.py
from typing import Optional
from datetime import datetime

class Message:
    def __init__(
        self,
        message_id: str,
        match_id: str,
        sender_id: str,
        receiver_id: str,
        content: str,
        sent_at: Optional[str] = None,
        read_at: Optional[str] = None,
        is_read: bool = False
    ):
        self.message_id = message_id
        self.match_id = match_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.sent_at = sent_at or datetime.utcnow().isoformat()
        self.read_at = read_at
        self.is_read = is_read
