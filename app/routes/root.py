# app/routes/root.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Dating API backend is running 🚀"}
