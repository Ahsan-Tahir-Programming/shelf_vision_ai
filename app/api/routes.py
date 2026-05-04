# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.core.analyzer import analyze_shelf_image
from app.core.rag import save_audit, get_store_history, get_database_stats
from app.agents.agent import create_shelf_agent
from app.models.schemas import (
    AnalyzeResponse, ChatResponse,
    HistoryResponse, AuditHistoryItem, StatsResponse
)
from datetime import datetime
from typing import Optional
import tempfile
import shutil
import os

router = APIRouter()

# In-memory store for active agent sessions
# Key: store_name, Value: agent instance
active_sessions: dict = {}

# ============================================================
# POST /api/analyze
# Upload shelf image → get compliance analysis
# ============================================================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_shelf(
    store_name: str = Form(...),
    notes: str = Form(""),
    image: UploadFile = File(...)
):
    """
    Accepts a shelf image upload and store name.
    Returns structured compliance analysis.
    """

    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (jpg, png, etc.)"
        )

    # Save uploaded image to temp file
    suffix = os.path.splitext(image.filename)[1] or ".jpg"
    os.makedirs("images", exist_ok=True)
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix, dir="images"
    ) as tmp:
        shutil.copyfileobj(image.file, tmp)
        tmp_path = tmp.name

    try:
        # Run Phase 2 analysis
        analysis = analyze_shelf_image(tmp_path)

        # Save to ChromaDB (Phase 4)
        record = save_audit(
            analysis=analysis,
            store_name=store_name.lower().strip(),
            image_path=tmp_path,
            notes=notes
        )

        # Create fresh agent session for this store (Phase 5)
        agent = create_shelf_agent(
            analysis=analysis,
            store_name=store_name.lower().strip()
        )
        active_sessions[store_name.lower().strip()] = {
            "agent": agent,
            "chat_history": [],
            "analysis": analysis
        }

        # Build zones dict for response
        zones_dict = {}
        for zone_name, zone_data in analysis.zones.items():
            zones_dict[zone_name] = {
                "status": zone_data.status,
                "products_present": zone_data.products_present,
                "details": zone_data.details
            }

        return AnalyzeResponse(
            audit_id=record.audit_id,
            store_name=store_name,
            compliance_score=analysis.compliance_score,
            summary=analysis.summary,
            brands_detected=analysis.brands_detected,
            violations=analysis.violations,
            recommendations=analysis.recommendations,
            zones=zones_dict,
            audit_date=record.audit_date
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

# ============================================================
# POST /api/chat
# Send message → get agent response
# ============================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    store_name: str = Form(...),
    message: str = Form(...)
):
    """
    Send a chat message about the analyzed shelf.
    Agent uses tools automatically when needed.
    """

    key = store_name.lower().strip()

    if key not in active_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"No active session for '{store_name}'. Please analyze an image first."
        )

    session = active_sessions[key]
    agent = session["agent"]
    chat_history = session["chat_history"]

    try:
        from langchain_core.messages import HumanMessage, AIMessage

        result = agent.invoke({
            "messages": [("user", message)]
        })

        last_message = result["messages"][-1]

        # Handle both string and list content
        if isinstance(last_message.content, str):
            response = last_message.content
        elif isinstance(last_message.content, list):
            response = " ".join(
                block.get("text", "")
                for block in last_message.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            response = str(last_message.content)

        # Update chat history
        chat_history.append(HumanMessage(content=message))
        chat_history.append(AIMessage(content=response))

        return ChatResponse(
            response=response,
            store_name=store_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# GET /api/history/{store_name}
# Get audit history for a store
# ============================================================

@router.get("/history/{store_name}", response_model=HistoryResponse)
async def get_history(store_name: str):
    """Returns all past audits for a specific store"""

    history = get_store_history(store_name.lower().strip())

    audits = []
    for audit in history:
        meta = audit["metadata"]
        audits.append(AuditHistoryItem(
            audit_id=audit["audit_id"],
            audit_date=meta.get("audit_date", ""),
            compliance_score=meta.get("compliance_score", 0),
            violations_count=meta.get("violations_count", 0),
            notes=meta.get("notes", "")
        ))

    return HistoryResponse(
        store_name=store_name,
        total_audits=len(audits),
        audits=audits
    )

# ============================================================
# GET /api/stats
# Get database-wide statistics
# ============================================================

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Returns statistics across all stores"""

    stats = get_database_stats()

    if stats["total_audits"] == 0:
        return StatsResponse(
            total_audits=0,
            stores=[],
            average_score=0.0,
            highest_score=0,
            lowest_score=0
        )

    return StatsResponse(
        total_audits=stats["total_audits"],
        stores=stats["stores"],
        average_score=stats.get("average_score", 0.0),
        highest_score=stats.get("highest_score", 0),
        lowest_score=stats.get("lowest_score", 0)
    )

# ============================================================
# GET /api/health
# Health check endpoint
# ============================================================

@router.get("/health")
async def health_check():
    """Simple health check — confirms API is running"""
    return {
        "status": "healthy",
        "service": "ShelfVision AI",
        "timestamp": datetime.now().isoformat()
    }