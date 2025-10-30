# app/routes/match.py
from fastapi import APIRouter, HTTPException
from app import crud
from app.schemas.Match import MatchResponse, MatchWithProfile
from typing import List

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: str):
    match = crud.Match.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match.__dict__

@router.get("/user/{user_id}", response_model=List[dict])
def get_user_matches(user_id: str):
    """Get all matches for a user"""
    print(f"Fetching matches for user: {user_id}")
    matches = crud.Match.get_user_matches(user_id)
    print(f"Found {len(matches)} matches: {matches}")
    return matches

@router.delete("/{match_id}")
def delete_match(match_id: str):
    """Unmatch users"""
    match = crud.Match.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Remove the match relationship from Neo4j
    from app.config import get_db
    session = get_db()
    query = "MATCH ()-[m:MATCHES {match_id: $match_id}]-() DELETE m"
    session.run(query, {"match_id": match_id})

    return {"message": "Match deleted successfully"}
