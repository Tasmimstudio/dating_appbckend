# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import User, Match, Swipe, Message, Photo, Interest, Block, Auth, Admin

app = FastAPI(title="Dating App Backend 🚀")

# ✅ Allow origins including all localhost ports you may use
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5176",
    "http://localhost:5177",
    "http://127.0.0.1:5177",
    "http://localhost:5183",
    "http://127.0.0.1:5183",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ✅ Enable CORS globally
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Optional: universal preflight handler
@app.options("/{path:path}")
async def preflight_handler(request: Request, path: str):
    origin = request.headers.get("origin", "http://localhost:5173")

    # Only allow our approved origins
    if origin not in origins:
        origin = "http://localhost:5173"

    response = JSONResponse(content={"message": "Preflight OK"}, status_code=200)
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = request.headers.get(
        "Access-Control-Request-Headers", "Authorization, Content-Type, Accept"
    )
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

# ✅ Routers
app.include_router(Auth.router, prefix="/auth", tags=["Auth"])
app.include_router(Admin.router)
app.include_router(User.router)
app.include_router(Match.router)
app.include_router(Swipe.router)
app.include_router(Message.router)
app.include_router(Photo.router)
app.include_router(Interest.router)
app.include_router(Block.router)

@app.get("/")
def root():
    return {"message": "Dating API backend is running 🚀"}
