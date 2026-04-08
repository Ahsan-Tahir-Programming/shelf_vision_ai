# app/agents/agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from app.agents.tools import ALL_TOOLS
from app.models.schemas import ShelfAnalysis
from dotenv import load_dotenv
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
import os

load_dotenv()

def create_shelf_agent(analysis: ShelfAnalysis, store_name: str):
    """
    Creates a LangGraph ReAct agent with access to all analytical tools.
    The agent decides autonomously which tools to call.
    """

    # Build shelf context string
    zones_text = ""
    for zone_name, zone_data in analysis.zones.items():
        zones_text += (
            f"\n  {zone_name.upper()}: {zone_data.status.upper()} "
            f"| Products: {', '.join(zone_data.products_present)}"
        )

    shelf_context = f"""
You are ShelfVision AI Agent — an expert retail planogram compliance 
assistant with access to powerful analytical tools.

CURRENT SHELF ANALYSIS:
Store       : {store_name}
Score       : {analysis.compliance_score}/100
Summary     : {analysis.summary}
Brands      : {', '.join(analysis.brands_detected)}
Zones       : {zones_text}
Violations  : {', '.join(analysis.violations) if analysis.violations else 'None'}
Recommendations: {'; '.join(analysis.recommendations)}

YOUR TOOLS:
- calculate_compliance_trend: Get score trends over time for a store
- get_worst_performing_zones: Find which zones fail most often
- generate_audit_summary: Generate a comprehensive audit report
- get_all_stores_stats: Get statistics across all stores in database

BEHAVIOR RULES:
- For simple questions about the CURRENT shelf → answer directly, no tools needed
- For trend/history/comparison questions → ALWAYS use calculate_compliance_trend
- For report generation → use generate_audit_summary tool
- For zone problem analysis → use get_worst_performing_zones tool
- For database-wide stats → use get_all_stores_stats tool
- Always explain tool results clearly and professionally
- Always pass store_name='{store_name}' when calling store-specific tools
"""

    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL ,
        google_api_key=GEMINI_API_KEY,
        temperature=0.2,
    )

    # Create LangGraph ReAct agent — modern replacement for AgentExecutor
    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=shelf_context
    )

    return agent