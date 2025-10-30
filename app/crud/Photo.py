# app/crud/photo.py
from app.config import get_db
from app.models.Photo import Photo
import uuid
from datetime import datetime

def create_photo(user_id: str, url: str, is_primary: bool = False, order: int = 0, public_id: str = None):
    session = get_db()
    try:
        photo_id = str(uuid.uuid4())

        # If this is a primary photo, unset other primary photos
        if is_primary:
            unset_query = """
            MATCH (p:Photo {user_id: $user_id, is_primary: true})
            SET p.is_primary = false
            """
            session.run(unset_query, {"user_id": user_id})

        query = """
        CREATE (p:Photo {
            photo_id: $photo_id,
            user_id: $user_id,
            url: $url,
            is_primary: $is_primary,
            order: $order,
            uploaded_at: $uploaded_at,
            public_id: $public_id
        })
        RETURN p
        """

        result = session.run(query, {
            "photo_id": photo_id,
            "user_id": user_id,
            "url": url,
            "is_primary": is_primary,
            "order": order,
            "uploaded_at": datetime.utcnow().isoformat(),
            "public_id": public_id
        })

        record = result.single()
        node = record["p"]

        return Photo(
            photo_id=node["photo_id"],
            user_id=node["user_id"],
            url=node["url"],
            is_primary=node["is_primary"],
            order=node["order"],
            uploaded_at=node["uploaded_at"],
            public_id=node.get("public_id")
        )
    finally:
        session.close()

def get_photo_by_id(photo_id: str):
    session = get_db()
    try:
        query = "MATCH (p:Photo {photo_id: $photo_id}) RETURN p"
        result = session.run(query, {"photo_id": photo_id}).single()

        if not result:
            return None

        node = result["p"]
        return Photo(
            photo_id=node["photo_id"],
            user_id=node["user_id"],
            url=node["url"],
            is_primary=node["is_primary"],
            order=node["order"],
            uploaded_at=node["uploaded_at"],
            public_id=node.get("public_id")
        )
    finally:
        session.close()

def get_user_photos(user_id: str):
    session = get_db()
    try:
        query = """
        MATCH (p:Photo {user_id: $user_id})
        RETURN p
        ORDER BY p.order ASC
        """
        results = session.run(query, {"user_id": user_id})

        photos = []
        for record in results:
            node = record["p"]
            photos.append(Photo(
                photo_id=node["photo_id"],
                user_id=node["user_id"],
                url=node["url"],
                is_primary=node["is_primary"],
                order=node["order"],
                uploaded_at=node["uploaded_at"],
                public_id=node.get("public_id")
            ))

        return photos
    finally:
        session.close()

def update_photo(photo_id: str, is_primary: bool = None, order: int = None):
    session = get_db()
    try:
        # Get photo first to get user_id
        photo = get_photo_by_id(photo_id)
        if not photo:
            return None

        # If setting as primary, unset other primary photos
        if is_primary:
            unset_query = """
            MATCH (p:Photo {user_id: $user_id, is_primary: true})
            SET p.is_primary = false
            """
            session.run(unset_query, {"user_id": photo.user_id})

        updates = []
        params = {"photo_id": photo_id}

        if is_primary is not None:
            updates.append("p.is_primary = $is_primary")
            params["is_primary"] = is_primary
        if order is not None:
            updates.append("p.order = $order")
            params["order"] = order

        if not updates:
            return photo

        query = f"MATCH (p:Photo {{photo_id: $photo_id}}) SET {', '.join(updates)} RETURN p"
        result = session.run(query, params).single()

        if not result:
            return None

        node = result["p"]
        return Photo(
            photo_id=node["photo_id"],
            user_id=node["user_id"],
            url=node["url"],
            is_primary=node["is_primary"],
            order=node["order"],
            uploaded_at=node["uploaded_at"],
            public_id=node.get("public_id")
        )
    finally:
        session.close()

def delete_photo(photo_id: str):
    session = get_db()
    try:
        query = "MATCH (p:Photo {photo_id: $photo_id}) DELETE p"
        session.run(query, {"photo_id": photo_id})
        return True
    finally:
        session.close()
