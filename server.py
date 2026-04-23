# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

# ── Initialize FastAPI app ──
app = FastAPI(
    title="ShelfVision AI API",
    description="Retail shelf compliance analysis powered by Gemini Vision + LangGraph",
    version="1.0.0"
)

# ── CORS — allows React frontend to call this API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React Vite dev server
        "http://localhost:3000",  # Alternative React port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register all routes under /api prefix ──
app.include_router(router, prefix="/api")


# ── Root endpoint ──
@app.get("/")
async def root():
    return {
        "message": "ShelfVision AI API is running",
        "docs": "/docs",
        "health": "/api/health"
    }