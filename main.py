# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import User, Match, Swipe, Message, Photo, Auth, Admin, Block, root  # import routers

app = FastAPI(title="Dating App Backend 🚀")

# ---------------------- CORS Setup ----------------------
origins = [
    "https://dating-app-frontend-zeta.vercel.app",                         # ✅ Vercel frontend
    "https://dating-app-frontend-tasmimstudioofficials-projects.vercel.app",  # ✅ alternative Vercel frontend
    "http://localhost:5173",                                               # ✅ local dev
    "http://127.0.0.1:5173",                                               # ✅ local IP
]

# Apply CORS middleware BEFORE any routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # list of allowed origins
    allow_credentials=True,   # allow cookies / auth headers
    allow_methods=["*"],      # allow all HTTP methods
    allow_headers=["*"],      # allow all headers
)

# ---------------------- Routers ----------------------
app.include_router(root.router)
app.include_router(Auth.router, prefix="/auth", tags=["Auth"])
app.include_router(Admin.router)
app.include_router(User.router)
app.include_router(Match.router)
app.include_router(Swipe.router)
app.include_router(Message.router)
app.include_router(Photo.router)
app.include_router(Block.router)

# ---------------------- Preflight OPTIONS route ----------------------
# Ensure OPTIONS requests return correct headers (helps on Render)
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return JSONResponse(status_code=200, content={"message": "preflight ok"})

# ---------------------- Health check route ----------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Dating API backend is running 🚀"}
