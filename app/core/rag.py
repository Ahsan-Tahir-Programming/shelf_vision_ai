# app/core/rag.py
import chromadb
from chromadb.config import Settings
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from google import genai
from app.core.config import GEMINI_API_KEY
from app.models.schemas import ShelfAnalysis, AuditRecord
from dotenv import load_dotenv
from datetime import datetime
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL, CHROMA_DB_PATH
from app.core.config import GEMINI_EMBEDDING_MODEL
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
import uuid
import json
import os

load_dotenv()

# ============================================================
# CHROMADB SETUP
# Persistent storage — data survives after program closes
# ============================================================

# Ensure directory exists
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# ============================================================
# CUSTOM EMBEDDING FUNCTION
# Uses new google.genai SDK — no deprecated library
# ============================================================

class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Custom ChromaDB embedding function using the new google.genai SDK.
    Converts text into vectors for semantic search in ChromaDB.
    """

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            result = self.client.models.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                contents=text
            )
            embeddings.append(result.embeddings[0].values)
        return embeddings

# Initialize ChromaDB with persistent storage
chroma_client = chromadb.PersistentClient(
    path=CHROMA_DB_PATH,
    settings=Settings(anonymized_telemetry=False)
)

# Use our custom Gemini embedding function
gemini_ef = GeminiEmbeddingFunction(api_key=GEMINI_API_KEY)

# Collection with our custom embedder
# Our collection — like a table in a database
# Each document = one shelf audit
audit_collection = chroma_client.get_or_create_collection(
    name="shelf_audits",
    embedding_function=gemini_ef,
    metadata={"description": "Retail shelf compliance audit history"}
)

# ============================================================
# SAVE AUDIT — Store a new audit in ChromaDB
# ============================================================

def save_audit(
    analysis: ShelfAnalysis,
    store_name: str,
    image_path: str,
    notes: str = ""
) -> AuditRecord:
    """
    Saves a shelf analysis to ChromaDB for future retrieval.
    This is called automatically every time a shelf is analyzed.
    
    ChromaDB stores 3 things per document:
    - document: text that gets embedded for semantic search
    - metadata: structured fields you can filter by
    - id: unique identifier
    """

    # Generate unique audit ID
    audit_id = str(uuid.uuid4())[:8].upper()
    audit_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Create AuditRecord
    record = AuditRecord(
        audit_id=audit_id,
        store_name=store_name,
        image_path=image_path,
        analysis=analysis,
        audit_date=audit_date,
        notes=notes
    )

    # ---- Build the TEXT document for embedding ----
    # This is what ChromaDB converts to a vector for semantic search
    # The richer the text, the better the search results
    violations_text = (
        "\n".join(f"- {v}" for v in analysis.violations)
        if analysis.violations else "- No violations found"
    )

    observations_text = "\n".join(
        f"- {o}" for o in analysis.positive_observations
    )

    recommendations_text = "\n".join(
        f"{i+1}. {r}" for i, r in enumerate(analysis.recommendations)
    )

    document_text = f"""
Store: {store_name}
Date: {audit_date}
Audit ID: {audit_id}
Compliance Score: {analysis.compliance_score}/100
Summary: {analysis.summary}

Brands Detected: {', '.join(analysis.brands_detected)}

Zone Results:
- Eye Level: {analysis.zones.get('eye_level', {}).status if hasattr(analysis.zones.get('eye_level', {}), 'status') else 'N/A'}
- Golden Zone: {analysis.zones.get('golden_zone', {}).status if hasattr(analysis.zones.get('golden_zone', {}), 'status') else 'N/A'}
- Top Shelf: {analysis.zones.get('top_shelf', {}).status if hasattr(analysis.zones.get('top_shelf', {}), 'status') else 'N/A'}
- Bottom Shelf: {analysis.zones.get('bottom_shelf', {}).status if hasattr(analysis.zones.get('bottom_shelf', {}), 'status') else 'N/A'}

Violations Found:
{violations_text}

Positive Observations:
{observations_text}

Recommendations:
{recommendations_text}

Notes: {notes if notes else 'None'}
"""

    # ---- Store in ChromaDB ----
    audit_collection.add(
        documents=[document_text],
        metadatas=[{
            "audit_id": audit_id,
            "store_name": store_name,
            "compliance_score": analysis.compliance_score,
            "audit_date": audit_date,
            "image_path": image_path,
            "violations_count": len(analysis.violations),
            "brands": ", ".join(analysis.brands_detected),
            # Store full analysis as JSON for retrieval
            "analysis_json": json.dumps(analysis.model_dump())
        }],
        ids=[audit_id]
    )

    print(f"💾 Audit saved to ChromaDB — ID: {audit_id}")
    return record


# ============================================================
# RETRIEVE RELEVANT AUDITS — Semantic search
# ============================================================

def retrieve_relevant_audits(
    query: str,
    store_name: str = None,
    n_results: int = 3
) -> list[dict]:
    """
    Searches ChromaDB for audits relevant to the query.
    Uses semantic similarity — not just keyword matching.

    For example:
    - "compliance trend" → finds audits with trend data
    - "violations in eye level" → finds audits with eye level issues
    - "Store A history" → finds all Store A audits
    """

    # Check if we have enough documents
    total_docs = audit_collection.count()
    if total_docs == 0:
        return []

    # Limit n_results to available documents
    n_results = min(n_results, total_docs)

    # Build where filter if store_name provided
    where_filter = None
    if store_name:
        where_filter = {"store_name": {"$eq": store_name}}

    # Semantic search
    results = audit_collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    # Format results for easy use
    formatted = []
    if results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            formatted.append({
                "document": doc,
                "metadata": results["metadatas"][0][i],
                "relevance_score": round(1 - results["distances"][0][i], 3)
            })

    return formatted


# ============================================================
# GET ALL AUDITS FOR A STORE
# ============================================================

def get_store_history(store_name: str) -> list[dict]:
    """
    Returns all audits for a specific store, sorted by date.
    Used for trend analysis.
    """

    total_docs = audit_collection.count()
    if total_docs == 0:
        return []

    results = audit_collection.get(
        where={"store_name": {"$eq": store_name}},
        include=["documents", "metadatas"]
    )

    if not results["ids"]:
        return []

    history = []
    for i, doc_id in enumerate(results["ids"]):
        history.append({
            "audit_id": doc_id,
            "document": results["documents"][i],
            "metadata": results["metadatas"][i]
        })

    # Sort by date (newest first)
    history.sort(
        key=lambda x: x["metadata"].get("audit_date", ""),
        reverse=True
    )

    return history


# ============================================================
# BUILD RAG CONTEXT — For injecting into chat
# ============================================================

def build_rag_context(query: str, store_name: str = None) -> str:
    """
    Retrieves relevant past audits and formats them
    as context to inject into the LLM conversation.

    This is the core of RAG — retrieve → format → inject.
    """

    relevant_audits = retrieve_relevant_audits(
        query=query,
        store_name=store_name,
        n_results=3
    )

    if not relevant_audits:
        return "No historical audit data available for comparison."

    context = "=== HISTORICAL AUDIT DATA (Retrieved from Database) ===\n\n"

    for i, audit in enumerate(relevant_audits, 1):
        meta = audit["metadata"]
        context += f"""
--- Past Audit {i} (Relevance: {audit['relevance_score']}) ---
Store: {meta.get('store_name', 'Unknown')}
Date: {meta.get('audit_date', 'Unknown')}
Score: {meta.get('compliance_score', 'N/A')}/100
Violations: {meta.get('violations_count', 0)} found
Brands: {meta.get('brands', 'N/A')}

Full Details:
{audit['document']}
"""

    context += "\n=== END OF HISTORICAL DATA ==="
    return context


# ============================================================
# STATS — Quick database summary
# ============================================================

def get_database_stats() -> dict:
    """Returns quick statistics about the audit database"""

    total = audit_collection.count()
    if total == 0:
        return {"total_audits": 0, "stores": [], "message": "No audits stored yet"}

    all_records = audit_collection.get(include=["metadatas"])
    stores = list(set(
        m.get("store_name", "Unknown")
        for m in all_records["metadatas"]
    ))
    scores = [
        m.get("compliance_score", 0)
        for m in all_records["metadatas"]
    ]

    return {
        "total_audits": total,
        "stores": stores,
        "average_score": round(sum(scores) / len(scores), 1),
        "highest_score": max(scores),
        "lowest_score": min(scores)
    }