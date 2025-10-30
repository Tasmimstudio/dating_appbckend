# app/models/swipe.py
from typing import Optional
from datetime import datetime

class Swipe:
    def __init__(
        self,
        swipe_id: str,
        from_user_id: str,
        to_user_id: str,
        action: str,
        timestamp: Optional[str] = None
    ):
        self.swipe_id = swipe_id
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.action = action
        self.timestamp = timestamp or datetime.utcnow().isoformat()
