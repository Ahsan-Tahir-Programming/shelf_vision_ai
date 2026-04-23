# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class ZoneAnalysis(BaseModel):
    """Analysis for a single shelf zone"""
    status: str = Field(description="pass or fail")
    products_present: list[str] = Field(description="List of products/brands found here")
    details: str = Field(description="Detailed assessment of this zone")

class ShelfAnalysis(BaseModel):
    """Complete structured analysis of a shelf image"""
    compliance_score: int = Field(description="Overall score from 0 to 100")
    summary: str = Field(description="One sentence summary of overall shelf condition")
    zones: dict[str, ZoneAnalysis] = Field(description="Analysis per zone")
    violations: list[str] = Field(description="List of specific violations found")
    positive_observations: list[str] = Field(description="List of things done well")
    recommendations: list[str] = Field(description="Top 3 prioritized recommendations")
    brands_detected: list[str] = Field(description="All brand names detected on shelf")

class AuditRecord(BaseModel):
    """A single audit record stored in the vector database"""
    audit_id: str = Field(description="Unique ID for this audit")
    store_name: str = Field(description="Name of the store")
    image_path: str = Field(description="Path to the shelf image")
    analysis: ShelfAnalysis = Field(description="Full structured analysis")
    audit_date: str = Field(description="Date of audit YYYY-MM-DD")
    notes: str = Field(default="", description="Optional manager notes")
    
# ── Request Models (what React sends to FastAPI) ──
class AnalyzeRequest(BaseModel):
    store_name: str
    notes: Optional[str] = ""

class ChatRequest(BaseModel):
    store_name: str
    message: str
    audit_id: Optional[str] = None

class HistoryRequest(BaseModel):
    store_name: str

# ── Response Models (what FastAPI sends back to React) ──

class AnalyzeResponse(BaseModel):
    audit_id: str
    store_name: str
    compliance_score: int
    summary: str
    brands_detected: list[str]
    violations: list[str]
    recommendations: list[str]
    zones: dict
    audit_date: str
    message: str = "Analysis complete"

class ChatResponse(BaseModel):
    response: str
    store_name: str

class AuditHistoryItem(BaseModel):
    audit_id: str
    audit_date: str
    compliance_score: int
    violations_count: int
    notes: str = ""

class HistoryResponse(BaseModel):
    store_name: str
    total_audits: int
    audits: list[AuditHistoryItem]

class StatsResponse(BaseModel):
    total_audits: int
    stores: list[str]
    average_score: float
    highest_score: int
    lowest_score: int
