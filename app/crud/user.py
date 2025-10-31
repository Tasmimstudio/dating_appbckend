# app/crud/user.py
from app.config import get_db
from app.models.User import User
import uuid
import bcrypt
from datetime import datetime

def create_user(user_data):
    session = get_db()
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
        interests: $interests,
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
        "interests": user_data.interests or [],
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
        interests=node.get("interests", []),
        is_verified=node.get("is_verified", False),
        created_at=node.get("created_at"),
        last_active=node.get("last_active"),
        min_age=node.get("min_age"),
        max_age=node.get("max_age"),
        max_distance=node.get("max_distance"),
        gender_preference=node.get("gender_preference", [])
    )

def get_user_by_id(user_id: str):
    session = get_db()
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
        interests=node.get("interests", []),
        is_verified=node.get("is_verified", False),
        created_at=node.get("created_at"),
        last_active=node.get("last_active"),
        min_age=node.get("min_age"),
        max_age=node.get("max_age"),
        max_distance=node.get("max_distance"),
        gender_preference=node.get("gender_preference", [])
    )

def update_user(user_id: str, user_data):
    session = get_db()

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
    if user_data.interests is not None:
        updates.append("u.interests = $interests")
        params["interests"] = user_data.interests
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
        interests=node.get("interests", []),
        is_verified=node.get("is_verified", False),
        created_at=node.get("created_at"),
        last_active=node.get("last_active"),
        min_age=node.get("min_age"),
        max_age=node.get("max_age"),
        max_distance=node.get("max_distance"),
        gender_preference=node.get("gender_preference", [])
    )

def get_user_by_email(email: str):
    session = get_db()
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
        interests=node.get("interests", []),
        is_verified=node.get("is_verified", False),
        created_at=node.get("created_at"),
        last_active=node.get("last_active"),
        min_age=node.get("min_age"),
        max_age=node.get("max_age"),
        max_distance=node.get("max_distance"),
        gender_preference=node.get("gender_preference", [])
    )

def get_potential_matches(user_id: str):
    """Get users that the user can swipe on (excluding already swiped users)"""
    import random
    session = get_db()

    query = """
    MATCH (u:User {user_id: $user_id})
    MATCH (other:User)
    WHERE other.user_id <> $user_id
    AND NOT (u)-[:SWIPED]->(other)
    OPTIONAL MATCH (other)<-[:BELONGS_TO]-(photo:Photo {is_primary: true})
    RETURN other, photo.url as primary_photo, rand() as random_order
    ORDER BY random_order
    LIMIT 50
    """

    result = session.run(query, {"user_id": user_id})

    users = []
    for record in result:
        node = record["other"]
        primary_photo = record.get("primary_photo")

        user_dict = {
            "user_id": node["user_id"],
            "name": node["name"],
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
            "interests": node.get("interests", []),
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

def search_users(query: str, limit: int = 20, current_user_id: str = None):
    """Search users by name or email"""
    session = get_db()

    # Case-insensitive search using CONTAINS and toLower
    # Exclude current user if provided
    if current_user_id:
        search_query = """
        MATCH (u:User)
        WHERE (toLower(u.name) CONTAINS toLower($query)
           OR toLower(u.email) CONTAINS toLower($query))
           AND u.user_id <> $current_user_id
        RETURN u
        LIMIT $limit
        """
        result = session.run(search_query, {"query": query, "limit": limit, "current_user_id": current_user_id})
    else:
        search_query = """
        MATCH (u:User)
        WHERE toLower(u.name) CONTAINS toLower($query)
           OR toLower(u.email) CONTAINS toLower($query)
        RETURN u
        LIMIT $limit
        """
        result = session.run(search_query, {"query": query, "limit": limit})

    users = []
    for record in result:
        node = record["u"]
        user = User(
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
            interests=node.get("interests", []),
            is_verified=node.get("is_verified", False),
            created_at=node.get("created_at"),
            last_active=node.get("last_active"),
            min_age=node.get("min_age"),
            max_age=node.get("max_age"),
            max_distance=node.get("max_distance"),
            gender_preference=node.get("gender_preference", [])
        )
        users.append(user)

    return users

def create_user_with_password(user_data: dict):
    """Create user with already hashed password"""
    session = get_db()
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
