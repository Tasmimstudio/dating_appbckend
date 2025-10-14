# app/crud/swipe.py
from app.config import get_db
from app.models.Swipe import Swipe
from app.crud.Match import create_match, check_mutual_like
import uuid
from datetime import datetime

def create_swipe(from_user_id: str, to_user_id: str, action: str):
    session = get_db()
    swipe_id = str(uuid.uuid4())

    # Create swipe relationship
    query = """
    MATCH (from:User {user_id: $from_user_id}), (to:User {user_id: $to_user_id})
    CREATE (from)-[s:SWIPED {
        swipe_id: $swipe_id,
        action: $action,
        timestamp: $timestamp
    }]->(to)
    RETURN s
    """

    result = session.run(query, {
        "from_user_id": from_user_id,
        "to_user_id": to_user_id,
        "swipe_id": swipe_id,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    })

    record = result.single()
    rel = record["s"]

    # If action is 'like' or 'super_like', create LIKES relationship
    is_match = False
    if action in ["like", "super_like"]:
        like_query = """
        MATCH (from:User {user_id: $from_user_id}), (to:User {user_id: $to_user_id})
        MERGE (from)-[:LIKES]->(to)
        """
        session.run(like_query, {"from_user_id": from_user_id, "to_user_id": to_user_id})
        print(f"Created LIKES relationship: {from_user_id} -> {to_user_id}")

        # Check for mutual like
        mutual = check_mutual_like(from_user_id, to_user_id)
        print(f"Checking mutual like between {from_user_id} and {to_user_id}: {mutual}")
        if mutual:
            # Create match
            print(f"Creating match between {from_user_id} and {to_user_id}")
            create_match(from_user_id, to_user_id)
            is_match = True
            print(f"Match created successfully!")

    swipe = Swipe(
        swipe_id=rel["swipe_id"],
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        action=rel["action"],
        timestamp=rel["timestamp"]
    )

    return {"swipe": swipe, "is_match": is_match}

def get_user_swipes(user_id: str, action: str = None):
    session = get_db()

    if action:
        query = """
        MATCH (u:User {user_id: $user_id})-[s:SWIPED {action: $action}]->(other:User)
        RETURN s, other.user_id as other_user_id
        ORDER BY s.timestamp DESC
        """
        results = session.run(query, {"user_id": user_id, "action": action})
    else:
        query = """
        MATCH (u:User {user_id: $user_id})-[s:SWIPED]->(other:User)
        RETURN s, other.user_id as other_user_id
        ORDER BY s.timestamp DESC
        """
        results = session.run(query, {"user_id": user_id})

    swipes = []
    for record in results:
        rel = record["s"]
        swipes.append({
            "swipe_id": rel["swipe_id"],
            "from_user_id": user_id,
            "to_user_id": record["other_user_id"],
            "action": rel["action"],
            "timestamp": rel["timestamp"]
        })

    return swipes

def check_already_swiped(from_user_id: str, to_user_id: str):
    """Check if user has already swiped on another user"""
    session = get_db()
    query = """
    MATCH (from:User {user_id: $from_user_id})-[s:SWIPED]->(to:User {user_id: $to_user_id})
    RETURN count(s) as swipe_count
    """
    result = session.run(query, {"from_user_id": from_user_id, "to_user_id": to_user_id}).single()

    return result["swipe_count"] > 0
