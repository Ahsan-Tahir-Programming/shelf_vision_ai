# app/core/chat.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.models.schemas import ShelfAnalysis
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.core.rag import build_rag_context

GEMINI_API_KEY = GEMINI_API_KEY
MODEL = GEMINI_MODEL

CHAT_SYSTEM_PROMPT = """
You are ShelfVision AI — an expert retail planogram compliance assistant 
with 10 years of experience in the FMCG and retail industry in Pakistan.

You have already analyzed a shelf image and have the full structured 
compliance report available as your context. You also have access to 
historical audit data from the database.

Your behavior:
- Answer questions based on the current shelf analysis AND historical data
- When asked about trends or comparisons, use the historical audit data
- Be specific, professional, and helpful
- Reference exact brands, zones, scores, and dates from the data
- If asked for reports, format them professionally
- Remember everything discussed in the conversation so far
- When giving action items, be specific and prioritized
"""

def build_context(analysis: ShelfAnalysis, store_name: str = None) -> str:
    """Combines current analysis + RAG history into one context"""

    zones_text = ""
    for zone_name, zone_data in analysis.zones.items():
        zones_text += f"""
  {zone_name.upper().replace('_', ' ')}:
    Status: {zone_data.status.upper()}
    Products: {', '.join(zone_data.products_present)}
    Details: {zone_data.details}
"""

    current = f"""
=== CURRENT SHELF ANALYSIS ===
COMPLIANCE SCORE: {analysis.compliance_score}/100
SUMMARY: {analysis.summary}
BRANDS DETECTED: {', '.join(analysis.brands_detected)}
ZONES:
{zones_text}
VIOLATIONS:
{chr(10).join(f'- {v}' for v in analysis.violations) if analysis.violations else '- None'}
RECOMMENDATIONS:
{chr(10).join(f'{i+1}. {r}' for i, r in enumerate(analysis.recommendations))}
=== END CURRENT ANALYSIS ===
"""

    # Pull historical context from ChromaDB
    rag_context = build_rag_context(
        query=f"compliance history for {store_name or 'this store'}",
        store_name=store_name
    )

    return current + "\n\n" + rag_context


class ShelfChatSession:
    """Manages a full conversation session with RAG support"""

    def __init__(self, analysis: ShelfAnalysis, store_name: str = "Unknown Store"):
        self.analysis = analysis
        self.store_name = store_name
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.3,
        )
        self.chat_history: list = [
            SystemMessage(
                content=CHAT_SYSTEM_PROMPT + "\n\n" + build_context(analysis, store_name)
            )
        ]

    def chat(self, user_message: str) -> str:
        """Send a message — RAG context is automatically included"""
        self.chat_history.append(HumanMessage(content=user_message))
        response = self.llm.invoke(self.chat_history)
        self.chat_history.append(AIMessage(content=response.content))
        return response.content

    def save_conversation(self, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("SHELFVISION AI — CONVERSATION LOG\n")
            f.write("=" * 50 + "\n\n")
            for message in self.chat_history:
                if isinstance(message, HumanMessage):
                    f.write(f"MANAGER: {message.content}\n\n")
                elif isinstance(message, AIMessage):
                    f.write(f"AI: {message.content}\n\n")
                    f.write("-" * 40 + "\n\n")