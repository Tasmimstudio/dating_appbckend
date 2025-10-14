# app/crud/interest.py
from app.config import get_db
from app.models.Interest import Interest
import uuid

def create_interest(name: str, category: str):
    session = get_db()
    interest_id = str(uuid.uuid4())

    query = """
    CREATE (i:Interest {
        interest_id: $interest_id,
        name: $name,
        category: $category
    })
    RETURN i
    """

    result = session.run(query, {
        "interest_id": interest_id,
        "name": name,
        "category": category
    })

    record = result.single()
    node = record["i"]

    return Interest(
        interest_id=node["interest_id"],
        name=node["name"],
        category=node["category"]
    )

def get_interest_by_id(interest_id: str):
    session = get_db()
    query = "MATCH (i:Interest {interest_id: $interest_id}) RETURN i"
    result = session.run(query, {"interest_id": interest_id}).single()

    if not result:
        return None

    node = result["i"]
    return Interest(
        interest_id=node["interest_id"],
        name=node["name"],
        category=node["category"]
    )

def get_all_interests(category: str = None):
    session = get_db()

    if category:
        query = "MATCH (i:Interest {category: $category}) RETURN i ORDER BY i.name"
        results = session.run(query, {"category": category})
    else:
        query = "MATCH (i:Interest) RETURN i ORDER BY i.name"
        results = session.run(query)

    interests = []
    for record in results:
        node = record["i"]
        interests.append(Interest(
            interest_id=node["interest_id"],
            name=node["name"],
            category=node["category"]
        ))

    return interests

def add_user_interest(user_id: str, interest_id: str):
    session = get_db()
    query = """
    MATCH (u:User {user_id: $user_id}), (i:Interest {interest_id: $interest_id})
    MERGE (u)-[:HAS_INTEREST]->(i)
    RETURN i
    """
    result = session.run(query, {"user_id": user_id, "interest_id": interest_id}).single()

    if not result:
        return None

    node = result["i"]
    return Interest(
        interest_id=node["interest_id"],
        name=node["name"],
        category=node["category"]
    )

def remove_user_interest(user_id: str, interest_id: str):
    session = get_db()
    query = """
    MATCH (u:User {user_id: $user_id})-[r:HAS_INTEREST]->(i:Interest {interest_id: $interest_id})
    DELETE r
    """
    session.run(query, {"user_id": user_id, "interest_id": interest_id})
    return True

def get_user_interests(user_id: str):
    session = get_db()
    query = """
    MATCH (u:User {user_id: $user_id})-[:HAS_INTEREST]->(i:Interest)
    RETURN i
    ORDER BY i.name
    """
    results = session.run(query, {"user_id": user_id})

    interests = []
    for record in results:
        node = record["i"]
        interests.append(Interest(
            interest_id=node["interest_id"],
            name=node["name"],
            category=node["category"]
        ))

    return interests

def get_users_by_interest(interest_id: str):
    """Get all users who have a specific interest"""
    session = get_db()
    query = """
    MATCH (u:User)-[:HAS_INTEREST]->(i:Interest {interest_id: $interest_id})
    RETURN u.user_id as user_id
    """
    results = session.run(query, {"interest_id": interest_id})

    user_ids = [record["user_id"] for record in results]
    return user_ids

def get_common_interests(user1_id: str, user2_id: str):
    """Get common interests between two users"""
    session = get_db()
    query = """
    MATCH (u1:User {user_id: $user1_id})-[:HAS_INTEREST]->(i:Interest)<-[:HAS_INTEREST]-(u2:User {user_id: $user2_id})
    RETURN i
    """
    results = session.run(query, {"user1_id": user1_id, "user2_id": user2_id})

    interests = []
    for record in results:
        node = record["i"]
        interests.append(Interest(
            interest_id=node["interest_id"],
            name=node["name"],
            category=node["category"]
        ))

    return interests
