# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import User, Match, Swipe, Message, Photo, Auth, Admin, WebSocket, Report, Block

app = FastAPI(title="Dating App Backend 🚀")

# ✅ Enable CORS globally - MUST be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://localhost:5180",
        "http://localhost:5181",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5181",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ✅ Routers
app.include_router(Auth.router, prefix="/auth", tags=["Auth"])
app.include_router(WebSocket.router, tags=["WebSocket"])
app.include_router(Admin.router)
app.include_router(User.router)
app.include_router(Match.router)
app.include_router(Swipe.router)
app.include_router(Message.router)
app.include_router(Photo.router)
app.include_router(Report.router)
app.include_router(Block.router)

@app.get("/")
def root():
    return {"message": "Dating API backend is running 🚀"}
