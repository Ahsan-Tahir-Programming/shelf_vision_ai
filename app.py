#!/usr/bin/env python
"""
Hugging Face Spaces app entry point for ShelfVision AI
Exposes FastAPI app for HF Spaces deployment
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the FastAPI app from server.py
from server import app

# Ensure required environment variables are set
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️  Warning: GEMINI_API_KEY not found in environment variables")
    print("   Please set it in Hugging Face Space secrets")

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 7860 (HF Spaces default)
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 ShelfVision AI Server starting on {host}:{port}")
    print(f"📚 API Docs available at http://localhost:{port}/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
