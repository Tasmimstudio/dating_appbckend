# app/crud/swipe.py
from app.config import get_db
from app.models.Swipe import Swipe
from app.crud.Match import create_match, check_mutual_like
import uuid
from datetime import datetime

def create_swipe(from_user_id: str, to_user_id: str, action: str):
    session = get_db()
    try:
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
    finally:
        session.close()

def get_user_swipes(user_id: str, action: str = None):
    session = get_db()
    try:
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
    finally:
        session.close()

def check_already_swiped(from_user_id: str, to_user_id: str):
    """Check if user has already swiped on another user"""
    session = get_db()
    try:
        query = """
        MATCH (from:User {user_id: $from_user_id})-[s:SWIPED]->(to:User {user_id: $to_user_id})
        RETURN count(s) as swipe_count
        """
        result = session.run(query, {"from_user_id": from_user_id, "to_user_id": to_user_id}).single()

        return result["swipe_count"] > 0
    finally:
        session.close()

def delete_swipe(swipe_id: str):
    """Delete a swipe by swipe_id"""
    session = get_db()
    try:
        # First get the swipe details before deleting
        get_query = """
        MATCH (from:User)-[s:SWIPED {swipe_id: $swipe_id}]->(to:User)
        RETURN s.action as action, from.user_id as from_user_id, to.user_id as to_user_id
        """
        result = session.run(get_query, {"swipe_id": swipe_id}).single()

        if not result:
            return {"success": False, "message": "Swipe not found"}

        action = result["action"]
        from_user_id = result["from_user_id"]
        to_user_id = result["to_user_id"]

        # Delete the SWIPED relationship
        delete_swipe_query = """
        MATCH (from:User)-[s:SWIPED {swipe_id: $swipe_id}]->(to:User)
        DELETE s
        """
        session.run(delete_swipe_query, {"swipe_id": swipe_id})

        # If it was a like or super_like, also remove the LIKES relationship
        if action in ["like", "super_like"]:
            delete_like_query = """
            MATCH (from:User {user_id: $from_user_id})-[l:LIKES]->(to:User {user_id: $to_user_id})
            DELETE l
            """
            session.run(delete_like_query, {"from_user_id": from_user_id, "to_user_id": to_user_id})

            # Also delete MATCHED_WITH relationship if it exists
            delete_match_query = """
            MATCH (from:User {user_id: $from_user_id})-[m:MATCHED_WITH]-(to:User {user_id: $to_user_id})
            DELETE m
            """
            session.run(delete_match_query, {"from_user_id": from_user_id, "to_user_id": to_user_id})

        return {"success": True, "message": "Swipe deleted successfully"}
    finally:
        session.close()
