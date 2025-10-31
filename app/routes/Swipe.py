# app/routes/swipe.py
from fastapi import APIRouter, HTTPException
from app import crud
from app.schemas.Swipe import SwipeCreate, SwipeResponse
from typing import List

router = APIRouter(prefix="/swipes", tags=["Swipes"])

@router.post("/", response_model=SwipeResponse)
def create_swipe(swipe: SwipeCreate):
    """Create a swipe (like, dislike, super_like)"""
    # Check if user has already swiped on this person
    already_swiped = crud.Swipe.check_already_swiped(swipe.from_user_id, swipe.to_user_id)
    if already_swiped:
        raise HTTPException(status_code=400, detail="You have already swiped on this user")

    # Check if users exist
    from_user = crud.user.get_user_by_id(swipe.from_user_id)
    to_user = crud.user.get_user_by_id(swipe.to_user_id)

    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create swipe
    result = crud.Swipe.create_swipe(swipe.from_user_id, swipe.to_user_id, swipe.action)

    return SwipeResponse(
        swipe_id=result["swipe"].swipe_id,
        from_user_id=result["swipe"].from_user_id,
        to_user_id=result["swipe"].to_user_id,
        action=result["swipe"].action,
        timestamp=result["swipe"].timestamp,
        is_match=result["is_match"]
    )

@router.get("/user/{user_id}", response_model=List[dict])
def get_user_swipes(user_id: str, action: str = None):
    """Get all swipes by a user, optionally filtered by action"""
    swipes = crud.Swipe.get_user_swipes(user_id, action)
    return swipes

@router.get("/likes/{user_id}", response_model=List[dict])
def get_user_likes(user_id: str):
    """Get users this user has liked in the last 24 hours (that haven't matched yet)"""
    from app.config import get_db
    from datetime import datetime, timedelta

    session = get_db()

    # Calculate 24 hours ago
    twenty_four_hours_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()

    # Get likes from last 24 hours that haven't matched
    query = """
    MATCH (u:User {user_id: $user_id})-[s:SWIPED]->(other:User)
    WHERE s.action IN ['like', 'super_like']
    AND s.timestamp >= $time_threshold
    AND NOT (u)-[:MATCHES]-(other)
    RETURN s.swipe_id as swipe_id,
           u.user_id as from_user_id,
           other.user_id as to_user_id,
           s.action as action,
           s.timestamp as timestamp
    ORDER BY s.timestamp DESC
    """

    results = session.run(query, {
        "user_id": user_id,
        "time_threshold": twenty_four_hours_ago
    })

    likes = []
    for record in results:
        likes.append({
            "swipe_id": record["swipe_id"],
            "from_user_id": record["from_user_id"],
            "to_user_id": record["to_user_id"],
            "action": record["action"],
            "timestamp": record["timestamp"]
        })

    return likes

@router.get("/received-likes/{user_id}")
def get_received_likes(user_id: str):
    """Get all users who liked this user (but not matched yet)"""
    from app.config import get_db
    session = get_db()

    # First, let's check ALL users who liked this user (for debugging)
    debug_query = """
    MATCH (other:User)-[:LIKES]->(u:User {user_id: $user_id})
    RETURN other.user_id as user_id, other.name as name,
           exists((u)-[:MATCHES]-(other)) as is_matched
    """
    debug_results = session.run(debug_query, {"user_id": user_id})
    all_likes = list(debug_results)
    print(f"DEBUG: User {user_id} has {len(all_likes)} total LIKES")
    for like in all_likes:
        print(f"  - {like['name']} (matched: {like['is_matched']})")

    # Get users who liked current user but aren't matched yet
    query = """
    MATCH (other:User)-[:LIKES]->(u:User {user_id: $user_id})
    WHERE NOT (u)-[:MATCHES]-(other)
    RETURN other.user_id as user_id, other.name as name, other.age as age, other.bio as bio
    ORDER BY other.name
    """
    results = session.run(query, {"user_id": user_id})

    received_likes = []
    for record in results:
        received_likes.append({
            "user_id": record["user_id"],
            "name": record["name"],
            "age": record.get("age"),
            "bio": record.get("bio")
        })

    print(f"User {user_id} has {len(received_likes)} unmatched received likes")
    return received_likes

@router.delete("/{swipe_id}")
def delete_swipe(swipe_id: str):
    """Delete a swipe (for undo functionality)"""
    result = crud.Swipe.delete_swipe(swipe_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])

    return {"message": result["message"]}
