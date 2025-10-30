# app/models/match.py
from typing import Optional
from datetime import datetime

class Match:
    def __init__(
        self,
        match_id: str,
        user1_id: str,
        user2_id: str,
        matched_at: Optional[str] = None,
        conversation_started: bool = False,
        last_message_at: Optional[str] = None
    ):
        self.match_id = match_id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.matched_at = matched_at or datetime.utcnow().isoformat()
        self.conversation_started = conversation_started
        self.last_message_at = last_message_at
