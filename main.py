# -*- coding: utf-8 -*-

# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import User, Match, Swipe, Message, Photo, Auth, Admin, Block, root  # import root router

app = FastAPI(title="Dating App Backend 🚀")

# ---------------------- CORS Setup ----------------------
# Enable CORS globally - must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dating-app-frontend-zeta.vercel.app",  # ✅ Vercel frontend
        "http://localhost:5173",                        # ✅ Local frontend
        "http://127.0.0.1:5173",                        # ✅ Local IP frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

# ---------------------- Routers ----------------------
app.include_router(Auth.router, prefix="/auth", tags=["Auth"])
app.include_router(Admin.router)
app.include_router(User.router)
app.include_router(Match.router)
app.include_router(Swipe.router)
app.include_router(Message.router)
app.include_router(Photo.router)
app.include_router(Block.router)
app.include_router(root.router)  # ✅ include root router

# Remove old root route from main.py
# @app.get("/")
# def root():
#     return {"message": "Dating API backend is running 🚀"}
