# app/crud/user.py
from app.config import get_db
from app.models.User import User
import uuid
import bcrypt
from datetime import datetime

def create_user(user_data):
    session = get_db()
    try:
        user_id = str(uuid.uuid4())

        # Hash password
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Prepare preferences
        preferences = user_data.preferences.dict() if user_data.preferences else {}

        query = """
        CREATE (u:User {
            user_id: $user_id,
            name: $name,
            email: $email,
            age: $age,
            gender: $gender,
            password_hash: $password_hash,
            bio: $bio,
            city: $city,
            latitude: $latitude,
            longitude: $longitude,
            height: $height,
            occupation: $occupation,
            education: $education,
            is_verified: $is_verified,
            created_at: $created_at,
            last_active: $last_active,
            min_age: $min_age,
            max_age: $max_age,
            max_distance: $max_distance,
            gender_preference: $gender_preference
        })
        RETURN u
        """

        result = session.run(query, {
            "user_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "age": user_data.age,
            "gender": user_data.gender,
            "password_hash": password_hash,
            "bio": user_data.bio,
            "city": user_data.city,
            "latitude": user_data.latitude,
            "longitude": user_data.longitude,
            "height": user_data.height,
            "occupation": user_data.occupation,
            "education": user_data.education,
            "is_verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
            "min_age": preferences.get("min_age"),
            "max_age": preferences.get("max_age"),
            "max_distance": preferences.get("max_distance"),
            "gender_preference": preferences.get("gender_preference", [])
        })

        record = result.single()
        node = record["u"]

        return User(
            user_id=node["user_id"],
            name=node["name"],
            email=node["email"],
            age=node["age"],
            gender=node["gender"],
            password_hash=node["password_hash"],
            bio=node.get("bio"),
            city=node.get("city"),
            latitude=node.get("latitude"),
            longitude=node.get("longitude"),
            height=node.get("height"),
            occupation=node.get("occupation"),
            education=node.get("education"),
            is_verified=node.get("is_verified", False),
            created_at=node.get("created_at"),
            last_active=node.get("last_active"),
            min_age=node.get("min_age"),
            max_age=node.get("max_age"),
            max_distance=node.get("max_distance"),
            gender_preference=node.get("gender_preference", [])
        )
    finally:
        session.close()

def get_user_by_id(user_id: str):
    session = get_db()
    try:
        query = "MATCH (u:User {user_id: $user_id}) RETURN u"
        result = session.run(query, {"user_id": user_id}).single()
        if not result:
            return None
        node = result["u"]

        return User(
            user_id=node["user_id"],
            name=node["name"],
            email=node["email"],
            age=node["age"],
            gender=node["gender"],
            password_hash=node["password_hash"],
            bio=node.get("bio"),
            city=node.get("city"),
            latitude=node.get("latitude"),
            longitude=node.get("longitude"),
            height=node.get("height"),
            occupation=node.get("occupation"),
            education=node.get("education"),
            is_verified=node.get("is_verified", False),
            created_at=node.get("created_at"),
            last_active=node.get("last_active"),
            min_age=node.get("min_age"),
            max_age=node.get("max_age"),
            max_distance=node.get("max_distance"),
            gender_preference=node.get("gender_preference", [])
        )
    finally:
        session.close()

def update_user(user_id: str, user_data):
    session = get_db()
    try:
        # Build dynamic update query
        updates = []
        params = {"user_id": user_id}

        if user_data.name is not None:
            updates.append("u.name = $name")
            params["name"] = user_data.name
        if user_data.bio is not None:
            updates.append("u.bio = $bio")
            params["bio"] = user_data.bio
        if user_data.city is not None:
            updates.append("u.city = $city")
            params["city"] = user_data.city
        if user_data.latitude is not None:
            updates.append("u.latitude = $latitude")
            params["latitude"] = user_data.latitude
        if user_data.longitude is not None:
            updates.append("u.longitude = $longitude")
            params["longitude"] = user_data.longitude
        if user_data.height is not None:
            updates.append("u.height = $height")
            params["height"] = user_data.height
        if user_data.occupation is not None:
            updates.append("u.occupation = $occupation")
            params["occupation"] = user_data.occupation
        if user_data.education is not None:
            updates.append("u.education = $education")
            params["education"] = user_data.education
        if user_data.preferences is not None:
            prefs = user_data.preferences.dict()
            updates.append("u.min_age = $min_age")
            updates.append("u.max_age = $max_age")
            updates.append("u.max_distance = $max_distance")
            updates.append("u.gender_preference = $gender_preference")
            params.update(prefs)

        if not updates:
            return get_user_by_id(user_id)

        query = f"MATCH (u:User {{user_id: $user_id}}) SET {', '.join(updates)} RETURN u"
        result = session.run(query, params).single()

        if not result:
            return None

        node = result["u"]
        return User(
            user_id=node["user_id"],
            name=node["name"],
            email=node["email"],
            age=node["age"],
            gender=node["gender"],
            password_hash=node["password_hash"],
            bio=node.get("bio"),
            city=node.get("city"),
            latitude=node.get("latitude"),
            longitude=node.get("longitude"),
            height=node.get("height"),
            occupation=node.get("occupation"),
            education=node.get("education"),
            is_verified=node.get("is_verified", False),
            created_at=node.get("created_at"),
            last_active=node.get("last_active"),
            min_age=node.get("min_age"),
            max_age=node.get("max_age"),
            max_distance=node.get("max_distance"),
            gender_preference=node.get("gender_preference", [])
        )
    finally:
        session.close()

def get_user_by_email(email: str):
    session = get_db()
    try:
        query = "MATCH (u:User {email: $email}) RETURN u"
        result = session.run(query, {"email": email}).single()
        if not result:
            return None
        node = result["u"]

        return User(
            user_id=node["user_id"],
            name=node["name"],
            email=node["email"],
            age=node["age"],
            gender=node["gender"],
            password_hash=node["password_hash"],
            bio=node.get("bio"),
            city=node.get("city"),
            latitude=node.get("latitude"),
            longitude=node.get("longitude"),
            height=node.get("height"),
            occupation=node.get("occupation"),
            education=node.get("education"),
            is_verified=node.get("is_verified", False),
            created_at=node.get("created_at"),
            last_active=node.get("last_active"),
            min_age=node.get("min_age"),
            max_age=node.get("max_age"),
            max_distance=node.get("max_distance"),
            gender_preference=node.get("gender_preference", [])
        )
    finally:
        session.close()

def get_potential_matches(user_id: str, min_age=None, max_age=None, gender_filter=None, max_distance=None, interests_filter=None):
    """Get users that the user can swipe on with optional filters"""
    import random
    session = get_db()
    try:
        # Build WHERE clauses dynamically
        where_clauses = [
            "other.user_id <> $user_id",
            "NOT (u)-[:SWIPED]->(other)"
        ]

        params = {"user_id": user_id}

        # Add age filters
        if min_age is not None:
            where_clauses.append("other.age >= $min_age")
            params["min_age"] = min_age
        if max_age is not None:
            where_clauses.append("other.age <= $max_age")
            params["max_age"] = max_age

        # Add gender filter
        if gender_filter:
            where_clauses.append("other.gender IN $gender_filter")
            params["gender_filter"] = gender_filter

        # TODO: Add distance filter when location data is fully implemented
        # TODO: Add interests filter when interests are added to user model

        where_clause_str = " AND ".join(where_clauses)

        query = f"""
        MATCH (u:User {{user_id: $user_id}})
        MATCH (other:User)
        WHERE {where_clause_str}
        OPTIONAL MATCH (other)<-[:BELONGS_TO]-(photo:Photo {{is_primary: true}})
        RETURN other, photo.url as primary_photo, rand() as random_order
        ORDER BY random_order
        LIMIT 50
        """

        result = session.run(query, params)

        users = []
        for record in result:
            node = record["other"]
            primary_photo = record.get("primary_photo")

            # Combine first_name and last_name into name, or use name if it exists
            if "name" in node and node["name"]:
                name = node["name"]
            elif "first_name" in node:
                first_name = node.get("first_name", "")
                last_name = node.get("last_name", "")
                name = f"{first_name} {last_name}".strip()
            else:
                name = "Unknown"

            user_dict = {
                "user_id": node["user_id"],
                "name": name,
                "email": node["email"],
                "age": node["age"],
                "gender": node["gender"],
                "bio": node.get("bio"),
                "city": node.get("city"),
                "latitude": node.get("latitude"),
                "longitude": node.get("longitude"),
                "height": node.get("height"),
                "occupation": node.get("occupation"),
                "education": node.get("education"),
                "is_verified": node.get("is_verified", False),
                "created_at": node.get("created_at"),
                "last_active": node.get("last_active"),
                "min_age": node.get("min_age"),
                "max_age": node.get("max_age"),
                "max_distance": node.get("max_distance"),
                "gender_preference": node.get("gender_preference", []),
                "primary_photo": primary_photo
            }
            users.append(user_dict)

        # Additional shuffle in Python for extra randomness
        random.shuffle(users)

        return users
    finally:
        session.close()

def create_user_with_password(user_data: dict):
    """Create user with already hashed password"""
    session = get_db()
    try:
        user_id = str(uuid.uuid4())

        query = """
        CREATE (u:User {
            user_id: $user_id,
            name: $name,
            email: $email,
            age: $age,
            gender: $gender,
            password_hash: $password_hash,
            bio: $bio,
            created_at: $created_at,
            last_active: $last_active
        })
        RETURN u
        """

        result = session.run(query, {
            "user_id": user_id,
            "name": user_data['name'],
            "email": user_data['email'],
            "age": user_data['age'],
            "gender": user_data['gender'],
            "password_hash": user_data.get('password_hash', user_data.get('password')),
            "bio": user_data.get('bio', ''),
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat()
        })

        record = result.single()
        node = record["u"]

        return User(
            user_id=node["user_id"],
            name=node["name"],
            email=node["email"],
            age=node["age"],
            gender=node["gender"],
            password_hash=node["password_hash"],
            bio=node.get("bio"),
            created_at=node.get("created_at"),
            last_active=node.get("last_active")
        )
    finally:
        session.close()
