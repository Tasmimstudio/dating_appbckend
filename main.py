# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import User, Match, Swipe, Message, Photo, Auth, Admin, Block, root  # import root router

app = FastAPI(title="Dating App Backend 🚀")

# ---------------------- CORS Setup ----------------------
origins = [
    "https://dating-app-frontend-zeta.vercel.app",  # ✅ Vercel frontend
    "https://dating-app-frontend-tasmimstudioofficials-projects.vercel.app"
    "http://localhost:5173",                        # ✅ Local frontend
    "http://127.0.0.1:5173",                        # ✅ Local IP frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

# ---------------------- Routers ----------------------
app.include_router(root.router)  # root route first
app.include_router(Auth.router, prefix="/auth", tags=["Auth"])
app.include_router(Admin.router)
app.include_router(User.router)
app.include_router(Match.router)
app.include_router(Swipe.router)
app.include_router(Message.router)
app.include_router(Photo.router)
app.include_router(Block.router)
