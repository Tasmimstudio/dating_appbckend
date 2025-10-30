# app/routes/Admin.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import timedelta
from app import crud
from app.auth import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])

# Admin credentials (in production, store securely in database)
ADMIN_CREDENTIALS = {
    "admin@datingapp.com": {
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5LS2LGYGzRMzK",  # "admin123"
        "role": "super_admin"
    }
}

class AdminLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserStats(BaseModel):
    total_users: int
    active_today: int
    new_this_week: int
    verified_users: int

# ---------- Admin Authentication ----------
@router.post("/login", response_model=Token)
def admin_login(credentials: AdminLogin):
    """Admin login endpoint"""
    admin = ADMIN_CREDENTIALS.get(credentials.email)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # For demo, allow "admin123" as password
    if credentials.password != "admin123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.email, "role": "admin"},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": admin["role"]
    }

# ---------- Dashboard Stats ----------
@router.get("/stats")
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        # Get all users for stats calculation
        from app.config import get_db
        session = get_db()

        # Total users
        total_result = session.run("MATCH (u:User) RETURN count(u) as total")
        total_users = total_result.single()["total"] if total_result.peek() else 0

        # Verified users
        verified_result = session.run("MATCH (u:User {is_verified: true}) RETURN count(u) as verified")
        verified_users = verified_result.single()["verified"] if verified_result.peek() else 0

        # Total matches
        matches_result = session.run("MATCH (m:Match) RETURN count(m) as matches")
        total_matches = matches_result.single()["matches"] if matches_result.peek() else 0

        # Total messages
        messages_result = session.run("MATCH (msg:Message) RETURN count(msg) as messages")
        total_messages = messages_result.single()["messages"] if messages_result.peek() else 0

        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "total_matches": total_matches,
            "total_messages": total_messages,
            "active_today": 0,  # TODO: implement with last_active tracking
            "new_this_week": 0  # TODO: implement with date filtering
        }
    except Exception as e:
        return {
            "total_users": 0,
            "verified_users": 0,
            "total_matches": 0,
            "total_messages": 0,
            "active_today": 0,
            "new_this_week": 0
        }

# ---------- User Management ----------
@router.get("/users")
def get_all_users(skip: int = 0, limit: int = 50):
    """Get all users with pagination"""
    try:
        from app.config import get_db
        session = get_db()

        query = """
        MATCH (u:User)
        RETURN u
        ORDER BY u.created_at DESC
        SKIP $skip
        LIMIT $limit
        """

        result = session.run(query, {"skip": skip, "limit": limit})
        users = []

        for record in result:
            node = record["u"]
            user_dict = dict(node)
            user_dict.pop("password_hash", None)  # Remove sensitive data
            users.append(user_dict)

        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    """Delete a user and all related data"""
    try:
        from app.config import get_db
        session = get_db()

        # Delete user and all relationships
        query = """
        MATCH (u:User {user_id: $user_id})
        DETACH DELETE u
        RETURN count(u) as deleted
        """

        result = session.run(query, {"user_id": user_id})
        deleted = result.single()["deleted"]

        if deleted == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/verify")
def verify_user(user_id: str):
    """Verify a user"""
    try:
        from app.config import get_db
        session = get_db()

        query = """
        MATCH (u:User {user_id: $user_id})
        SET u.is_verified = true
        RETURN u
        """

        result = session.run(query, {"user_id": user_id})
        if not result.peek():
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User verified successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/ban")
def ban_user(user_id: str):
    """Ban a user"""
    try:
        from app.config import get_db
        session = get_db()

        query = """
        MATCH (u:User {user_id: $user_id})
        SET u.is_banned = true, u.banned_at = $banned_at
        RETURN u
        """

        from datetime import datetime
        result = session.run(query, {
            "user_id": user_id,
            "banned_at": datetime.utcnow().isoformat()
        })

        if not result.peek():
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User banned successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Match Management ----------
@router.get("/matches")
def get_all_matches(skip: int = 0, limit: int = 50):
    """Get all matches"""
    try:
        from app.config import get_db
        session = get_db()

        query = """
        MATCH (m:Match)
        RETURN m
        ORDER BY m.matched_at DESC
        SKIP $skip
        LIMIT $limit
        """

        result = session.run(query, {"skip": skip, "limit": limit})
        matches = []

        for record in result:
            matches.append(dict(record["m"]))

        return {"matches": matches, "count": len(matches)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/matches/{match_id}")
def delete_match(match_id: str):
    """Delete a match"""
    try:
        from app.config import get_db
        session = get_db()

        query = """
        MATCH (m:Match {match_id: $match_id})
        DETACH DELETE m
        RETURN count(m) as deleted
        """

        result = session.run(query, {"match_id": match_id})
        deleted = result.single()["deleted"]

        if deleted == 0:
            raise HTTPException(status_code=404, detail="Match not found")

        return {"message": "Match deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Reports & Analytics ----------
@router.get("/analytics/users-growth")
def get_users_growth():
    """Get user growth analytics"""
    try:
        from app.config import get_db
        session = get_db()

        # This is a simplified version - in production, group by date
        query = """
        MATCH (u:User)
        RETURN u.created_at as date, count(u) as count
        ORDER BY u.created_at DESC
        LIMIT 30
        """

        result = session.run(query)
        growth_data = [{"date": record["date"], "count": record["count"]} for record in result]

        return {"growth": growth_data}
    except Exception as e:
        return {"growth": []}

@router.get("/analytics/match-rate")
def get_match_rate():
    """Get match rate analytics"""
    try:
        from app.config import get_db
        session = get_db()

        # Get total swipes and matches
        swipes_query = "MATCH (s:Swipe) RETURN count(s) as total_swipes"
        matches_query = "MATCH (m:Match) RETURN count(m) as total_matches"

        swipes_result = session.run(swipes_query)
        matches_result = session.run(matches_query)

        total_swipes = swipes_result.single()["total_swipes"] if swipes_result.peek() else 0
        total_matches = matches_result.single()["total_matches"] if matches_result.peek() else 0

        match_rate = (total_matches / total_swipes * 100) if total_swipes > 0 else 0

        return {
            "total_swipes": total_swipes,
            "total_matches": total_matches,
            "match_rate": round(match_rate, 2)
        }
    except Exception as e:
        return {
            "total_swipes": 0,
            "total_matches": 0,
            "match_rate": 0
        }
