# app/routes/Block.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.config import get_db

router = APIRouter(prefix="/blocks", tags=["Blocks"])

class BlockCreate(BaseModel):
    blocker_id: str
    blocked_id: str
    reason: str = None

@router.post("/")
def block_user(block: BlockCreate):
    """Block a user"""
    session = get_db()

    # Check if already blocked
    check_query = """
    MATCH (blocker:User {user_id: $blocker_id})-[b:BLOCKED]->(blocked:User {user_id: $blocked_id})
    RETURN b
    """

    result = session.run(check_query, {
        "blocker_id": block.blocker_id,
        "blocked_id": block.blocked_id
    })

    if result.single():
        raise HTTPException(status_code=400, detail="User is already blocked")

    # Create BLOCKED relationship
    query = """
    MATCH (blocker:User {user_id: $blocker_id})
    MATCH (blocked:User {user_id: $blocked_id})
    CREATE (blocker)-[b:BLOCKED {
        reason: $reason,
        blocked_at: $blocked_at
    }]->(blocked)

    // Remove any existing MATCHES relationship
    OPTIONAL MATCH (blocker)-[m:MATCHES]-(blocked)
    DELETE m

    RETURN b, blocked.user_id as blocked_user_id, blocked.name as blocked_name
    """

    result = session.run(query, {
        "blocker_id": block.blocker_id,
        "blocked_id": block.blocked_id,
        "reason": block.reason,
        "blocked_at": datetime.utcnow().isoformat()
    })

    record = result.single()
    if not record:
        raise HTTPException(status_code=404, detail="One or both users not found")

    return {
        "message": "User blocked successfully",
        "blocked_user_id": record["blocked_user_id"],
        "blocked_name": record["blocked_name"]
    }

@router.delete("/{blocker_id}/{blocked_id}")
def unblock_user(blocker_id: str, blocked_id: str):
    """Unblock a user"""
    session = get_db()

    query = """
    MATCH (blocker:User {user_id: $blocker_id})-[b:BLOCKED]->(blocked:User {user_id: $blocked_id})
    DELETE b
    RETURN count(b) as unblocked_count
    """

    result = session.run(query, {
        "blocker_id": blocker_id,
        "blocked_id": blocked_id
    })

    record = result.single()
    if not record or record["unblocked_count"] == 0:
        raise HTTPException(status_code=404, detail="Block relationship not found")

    return {"message": "User unblocked successfully"}

@router.get("/user/{user_id}")
def get_blocked_users(user_id: str):
    """Get all users blocked by this user"""
    session = get_db()

    query = """
    MATCH (u:User {user_id: $user_id})-[b:BLOCKED]->(blocked:User)
    OPTIONAL MATCH (blocked)<-[:BELONGS_TO]-(photo:Photo {is_primary: true})
    RETURN blocked.user_id as user_id, blocked.name as name, blocked.age as age,
           blocked.bio as bio, photo.url as primary_photo, b.blocked_at as blocked_at, b.reason as reason
    ORDER BY b.blocked_at DESC
    """

    result = session.run(query, {"user_id": user_id})

    blocked_users = []
    for record in result:
        blocked_users.append({
            "user_id": record["user_id"],
            "name": record["name"],
            "age": record.get("age"),
            "bio": record.get("bio"),
            "primary_photo": record.get("primary_photo"),
            "blocked_at": record["blocked_at"],
            "reason": record.get("reason")
        })

    return blocked_users
