# app/models/photo.py
from typing import Optional
from datetime import datetime

class Photo:
    def __init__(
        self,
        photo_id: str,
        user_id: str,
        url: str,
        is_primary: bool = False,
        order: int = 0,
        uploaded_at: Optional[str] = None,
        public_id: Optional[str] = None
    ):
        self.photo_id = photo_id
        self.user_id = user_id
        self.url = url
        self.is_primary = is_primary
        self.order = order
        self.uploaded_at = uploaded_at or datetime.utcnow().isoformat()
        self.public_id = public_id  # Cloudinary public_id for deletion
