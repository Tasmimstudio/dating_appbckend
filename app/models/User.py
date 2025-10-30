# app/models/user.py
from typing import Optional, List
from datetime import datetime

class User:
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        age: int,
        gender: str,
        password_hash: Optional[str] = None,
        password: Optional[str] = None,
        bio: Optional[str] = None,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        height: Optional[int] = None,
        occupation: Optional[str] = None,
        education: Optional[str] = None,
        is_verified: bool = False,
        created_at: Optional[str] = None,
        last_active: Optional[str] = None,
        # Preferences
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        max_distance: Optional[int] = None,
        gender_preference: Optional[List[str]] = None
    ):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age
        self.gender = gender
        self.password_hash = password_hash
        self.password = password or password_hash
        self.bio = bio
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
        self.height = height
        self.occupation = occupation
        self.education = education
        self.is_verified = is_verified
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.last_active = last_active or datetime.utcnow().isoformat()
        self.min_age = min_age
        self.max_age = max_age
        self.max_distance = max_distance
        self.gender_preference = gender_preference or []
