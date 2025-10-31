# -*- coding: utf-8 -*-

# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import User, Match, Swipe, Message, Photo, Auth, Admin, Block

app = FastAPI(title="Dating App Backend 🚀")

# ---------------------- CORS Setup ----------------------
# Enable CORS globally - must be added before routes
# Temporarily allow all origins to debug preflight issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=[  # Replace "*" with your frontend URL in production
        "*",  
        "https://dating-app-frontend-zeta.vercel.app",  # ✅ Vercel frontend
        "http://localhost:5173",                        # ✅ Local frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
    expose_headers=["*"],
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

# ---------------------- Root ----------------------
@app.get("/")
def root():
    return {"message": "Dating API backend is running 🚀"}
