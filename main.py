# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import User, Match, Swipe, Message, Photo, Auth, Admin, Block, root
import os

app = FastAPI(title="Dating App Backend 🚀")

# ---------------------- CORS Setup ----------------------
# Allow frontend domains
origins = [
    "https://dating-app-frontend-tasmimstudioofficials-projects.vercel.app",  # Vercel frontend
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(root.router)

# ---------------------- Optional root route ----------------------
@app.get("/")
def root_endpoint():
    return {"message": "Dating API backend is running 🚀"}


# ---------------------- Run server ----------------------
# Only needed if running main.py directly
if __name__ == "__main__":
    import uvicorn

    # Use PORT from Render environment variable, fallback to 8000 for local
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
