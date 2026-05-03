# server.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
    # previous 
    # allow_origins=[
    #     "http://localhost:5173",  # React Vite dev server
    #     "http://localhost:3000",  # Alternative React port
    # ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register all routes under /api prefix ──
app.include_router(router, prefix="/api")

# ── Serve React build files (production) ──
# This makes FastAPI serve your React app
FRONTEND_BUILD = "frontend/dist"

if os.path.exists(FRONTEND_BUILD):
    app.mount(
        "/assets",
        StaticFiles(directory=f"{FRONTEND_BUILD}/assets"),
        name="assets"
    )

    @app.get("/")
    async def serve_react():
        return FileResponse(f"{FRONTEND_BUILD}/index.html")

    @app.get("/{full_path:path}")
    async def serve_react_routes(full_path: str):
        # For any non-API route, serve React's index.html
        index = f"{FRONTEND_BUILD}/index.html"
        if os.path.exists(index):
            return FileResponse(index)

# ── Root endpoint ──
@app.get("/")
async def root():
    return {
        "message": "ShelfVision AI API is running",
        "docs": "/docs",
        "health": "/api/health"
    }