# -*- coding: utf-8 -*-

# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import User, Match, Swipe, Message, Photo, Auth, Admin, Block
app = FastAPI(title="Dating App Backend 🚀")

# ✅ Enable CORS globally - MUST be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        
        "https://dating-app-frontend-zeta.vercel.app",  # ✅ your Vercel domain
        "http://localhost:5173",  # ✅ for local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ✅ Routers
app.include_router(Auth.router, prefix="/auth", tags=["Auth"])
app.include_router(Admin.router)
app.include_router(User.router)
app.include_router(Match.router)
app.include_router(Swipe.router)
app.include_router(Message.router)
app.include_router(Photo.router)
app.include_router(Block.router)

@app.get("/")
def root():
    return {"message": "Dating API backend is running 🚀"}
