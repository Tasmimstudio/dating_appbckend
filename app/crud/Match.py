# app/crud/match.py
from app.config import get_db
from app.models.Match import Match
import uuid
from datetime import datetime

def create_match(user1_id: str, user2_id: str):
    session = get_db()
    try:
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
    finally:
        session.close()

def get_match_by_id(match_id: str):
    session = get_db()
    try:
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
    finally:
        session.close()

def get_user_matches(user_id: str):
    session = get_db()
    try:
        query = """
        MATCH (u:User {user_id: $user_id})-[m:MATCHES]-(other:User)
        RETURN m, other
        ORDER BY m.matched_at DESC
        """
        results = session.run(query, {"user_id": user_id})

        matches = []
        for record in results:
            rel = record["m"]
            other_user = record["other"]
            matches.append({
                "match_id": rel["match_id"],
                "user_id": other_user["user_id"],
                "name": other_user["name"],
                "age": other_user.get("age"),
                "bio": other_user.get("bio"),
                "gender": other_user.get("gender"),
                "location": other_user.get("location"),
                "matched_at": rel["matched_at"],
                "conversation_started": rel["conversation_started"],
                "last_message_at": rel.get("last_message_at")
            })

        return matches
    finally:
        session.close()

def update_match_conversation_status(match_id: str, started: bool = True):
    session = get_db()
    try:
        query = """
        MATCH ()-[m:MATCHES {match_id: $match_id}]-()
        SET m.conversation_started = $started
        RETURN m
        """
        result = session.run(query, {"match_id": match_id, "started": started}).single()

        if not result:
            return None

        return True
    finally:
        session.close()

def check_mutual_like(user1_id: str, user2_id: str):
    """Check if two users have liked each other"""
    session = get_db()
    try:
        query = """
        MATCH (u1:User {user_id: $user1_id})-[:LIKES]->(u2:User {user_id: $user2_id})
        MATCH (u2)-[:LIKES]->(u1)
        RETURN count(*) as mutual_like
        """
        result = session.run(query, {"user1_id": user1_id, "user2_id": user2_id}).single()

        return result["mutual_like"] > 0
    finally:
        session.close()
