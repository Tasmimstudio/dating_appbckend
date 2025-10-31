# app/crud/match.py
from app.config import get_db
from app.models.Match import Match
import uuid
from datetime import datetime

def create_match(user1_id: str, user2_id: str):
    session = get_db()
    match_id = str(uuid.uuid4())

    query = """
    MATCH (u1:User {user_id: $user1_id}), (u2:User {user_id: $user2_id})
    CREATE (u1)-[m:MATCHES {
        match_id: $match_id,
        matched_at: $matched_at,
        conversation_started: false,
        last_message_at: null
    }]->(u2)
    RETURN m
    """

    result = session.run(query, {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "match_id": match_id,
        "matched_at": datetime.utcnow().isoformat()
    })

    record = result.single()
    rel = record["m"]

    return Match(
        match_id=rel["match_id"],
        user1_id=user1_id,
        user2_id=user2_id,
        matched_at=rel["matched_at"],
        conversation_started=rel["conversation_started"],
        last_message_at=rel.get("last_message_at")
    )

def get_match_by_id(match_id: str):
    session = get_db()
    query = """
    MATCH (u1:User)-[m:MATCHES {match_id: $match_id}]->(u2:User)
    RETURN m, u1.user_id as user1_id, u2.user_id as user2_id
    """
    result = session.run(query, {"match_id": match_id}).single()

    if not result:
        return None

    rel = result["m"]
    return Match(
        match_id=rel["match_id"],
        user1_id=result["user1_id"],
        user2_id=result["user2_id"],
        matched_at=rel["matched_at"],
        conversation_started=rel["conversation_started"],
        last_message_at=rel.get("last_message_at")
    )

def get_user_matches(user_id: str):
    session = get_db()
    query = """
    MATCH (u:User {user_id: $user_id})-[m:MATCHES]-(other:User)
    OPTIONAL MATCH (other)<-[:BELONGS_TO]-(photo:Photo {is_primary: true})
    OPTIONAL MATCH (msg:Message)
    WHERE (msg.sender_id = $user_id AND msg.receiver_id = other.user_id)
       OR (msg.sender_id = other.user_id AND msg.receiver_id = $user_id)
    WITH m, other, photo, msg
    ORDER BY msg.sent_at DESC
    WITH m, other, photo.url as primary_photo,
         COLLECT(msg)[0] as lastMsg
    RETURN m, other, primary_photo,
           lastMsg.content as last_message,
           lastMsg.sent_at as last_message_time
    ORDER BY COALESCE(lastMsg.sent_at, m.matched_at) DESC
    """
    results = session.run(query, {"user_id": user_id})

    matches = []
    for record in results:
        rel = record["m"]
        other_user = record["other"]
        matches.append({
            "match_id": rel["match_id"],
            "other_user_id": other_user["user_id"],
            "other_user_name": other_user["name"],
            "other_user": {
                "user_id": other_user["user_id"],
                "name": other_user["name"],
                "age": other_user.get("age"),
                "gender": other_user.get("gender"),
                "bio": other_user.get("bio"),
                "city": other_user.get("city"),
                "occupation": other_user.get("occupation"),
                "primary_photo": record.get("primary_photo")
            },
            "matched_at": rel["matched_at"],
            "conversation_started": rel["conversation_started"],
            "last_message_at": rel.get("last_message_at"),
            "last_message": record.get("last_message"),
            "last_message_time": record.get("last_message_time")
        })

    return matches

def update_match_conversation_status(match_id: str, started: bool = True):
    session = get_db()
    query = """
    MATCH ()-[m:MATCHES {match_id: $match_id}]-()
    SET m.conversation_started = $started
    RETURN m
    """
    result = session.run(query, {"match_id": match_id, "started": started}).single()

    if not result:
        return None

    return True

def check_mutual_like(user1_id: str, user2_id: str):
    """Check if two users have liked each other"""
    session = get_db()
    query = """
    MATCH (u1:User {user_id: $user1_id})-[:LIKES]->(u2:User {user_id: $user2_id})
    MATCH (u2)-[:LIKES]->(u1)
    RETURN count(*) as mutual_like
    """
    result = session.run(query, {"user1_id": user1_id, "user2_id": user2_id}).single()

    return result["mutual_like"] > 0
