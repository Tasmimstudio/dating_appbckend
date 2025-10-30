# app/routes/user.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.crud import user as crud_user
from app.schemas.User import UserCreate, UserResponse, UserUpdate
from typing import List, Optional

router = APIRouter(prefix="/users", tags=["Users"])

# ========== Interest Management Schemas ==========
class InterestsUpdate(BaseModel):
    interests: List[str]

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    new_user = crud_user.create_user(user)
    return new_user.__dict__

@router.get("/search/by-name")
def search_users_by_name(
    query: str = Query(..., min_length=1, description="Search query for name"),
    current_user_id: str = Query(..., description="ID of the user performing the search"),
    limit: int = Query(20, description="Maximum number of results")
):
    """Search for users by name"""
    from app.config import get_db
    session = get_db()

    # Search for users by name (case-insensitive)
    search_query = """
    MATCH (u:User)
    WHERE toLower(u.name) CONTAINS toLower($query)
    AND u.user_id <> $current_user_id
    OPTIONAL MATCH (u)<-[:BELONGS_TO]-(photo:Photo {is_primary: true})
    RETURN u, photo.url as primary_photo
    ORDER BY u.name
    LIMIT $limit
    """

    result = session.run(search_query, {
        "query": query,
        "current_user_id": current_user_id,
        "limit": limit
    })

    users = []
    for record in result:
        node = record["u"]
        users.append({
            "user_id": node["user_id"],
            "name": node["name"],
            "age": node.get("age"),
            "gender": node.get("gender"),
            "bio": node.get("bio"),
            "city": node.get("city"),
            "occupation": node.get("occupation"),
            "primary_photo": record.get("primary_photo")
        })

    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.__dict__

@router.get("/{user_id}/potential-matches")
def get_potential_matches(
    user_id: str,
    min_age: Optional[int] = Query(None, description="Minimum age filter"),
    max_age: Optional[int] = Query(None, description="Maximum age filter"),
    gender: Optional[str] = Query(None, description="Gender filter (comma-separated for multiple)"),
    max_distance: Optional[int] = Query(None, description="Maximum distance in km"),
    interests: Optional[str] = Query(None, description="Interests filter (comma-separated)"),
):
    """Get users that this user can swipe on with optional filters"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Parse comma-separated values
    gender_list = gender.split(',') if gender else None
    interests_list = interests.split(',') if interests else None

    # Get filtered potential matches
    potential_matches = crud_user.get_potential_matches(
        user_id,
        min_age=min_age,
        max_age=max_age,
        gender_filter=gender_list,
        max_distance=max_distance,
        interests_filter=interests_list
    )
    return potential_matches

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_update: UserUpdate):
    """Update user profile"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = crud_user.update_user(user_id, user_update)
    return updated_user.__dict__

# ========== Interest Management Endpoints ==========

@router.get("/{user_id}/interests")
def get_user_interests(user_id: str):
    """Get all interests for a user"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.config import get_db
    session = get_db()

    query = """
    MATCH (u:User {user_id: $user_id})-[:INTERESTED_IN]->(i:Interest)
    RETURN i.id as id, i.name as name, i.emoji as emoji
    ORDER BY i.name
    """

    result = session.run(query, {"user_id": user_id})

    interests = []
    for record in result:
        interests.append({
            "id": record["id"],
            "name": record["name"],
            "emoji": record["emoji"]
        })

    return {"interests": interests}

@router.put("/{user_id}/interests")
def update_user_interests(user_id: str, interests_data: InterestsUpdate):
    """Update user interests (replaces all existing interests)"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if len(interests_data.interests) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 interests allowed")

    from app.config import get_db
    session = get_db()

    # Delete all existing interests
    delete_query = """
    MATCH (u:User {user_id: $user_id})-[r:INTERESTED_IN]->(:Interest)
    DELETE r
    """
    session.run(delete_query, {"user_id": user_id})

    # Add new interests
    if interests_data.interests:
        for interest_id in interests_data.interests:
            # Create interest node if it doesn't exist and create relationship
            create_query = """
            MATCH (u:User {user_id: $user_id})
            MERGE (i:Interest {id: $interest_id})
            ON CREATE SET i.name = $interest_id, i.emoji = ''
            MERGE (u)-[:INTERESTED_IN]->(i)
            RETURN i
            """
            session.run(create_query, {
                "user_id": user_id,
                "interest_id": interest_id
            })

    return {
        "message": "Interests updated successfully",
        "interests": interests_data.interests
    }

@router.post("/{user_id}/interests")
def add_user_interests(user_id: str, interests_data: InterestsUpdate):
    """Add interests to user (keeps existing interests)"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.config import get_db
    session = get_db()

    # Check current interest count
    count_query = """
    MATCH (u:User {user_id: $user_id})-[:INTERESTED_IN]->(:Interest)
    RETURN count(*) as count
    """
    count_result = session.run(count_query, {"user_id": user_id})
    current_count = count_result.single()["count"]

    if current_count + len(interests_data.interests) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 interests allowed")

    # Add new interests
    for interest_id in interests_data.interests:
        create_query = """
        MATCH (u:User {user_id: $user_id})
        MERGE (i:Interest {id: $interest_id})
        ON CREATE SET i.name = $interest_id, i.emoji = ''
        MERGE (u)-[:INTERESTED_IN]->(i)
        RETURN i
        """
        session.run(create_query, {
            "user_id": user_id,
            "interest_id": interest_id
        })

    return {
        "message": "Interests added successfully",
        "added": interests_data.interests
    }

@router.delete("/{user_id}/interests/{interest_id}")
def remove_user_interest(user_id: str, interest_id: str):
    """Remove a specific interest from user"""
    user = crud_user.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app.config import get_db
    session = get_db()

    query = """
    MATCH (u:User {user_id: $user_id})-[r:INTERESTED_IN]->(i:Interest {id: $interest_id})
    DELETE r
    RETURN count(r) as deleted
    """

    result = session.run(query, {
        "user_id": user_id,
        "interest_id": interest_id
    })

    deleted = result.single()["deleted"]

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Interest not found for this user")

    return {"message": "Interest removed successfully"}
