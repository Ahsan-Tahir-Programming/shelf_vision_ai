from google import genai as google_genai
from google.genai import types
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from PIL import Image
import os
import io
import json

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Google genai client (for image analysis - same as Phase 2)
google_client = google_genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# PYDANTIC MODELS (same as Phase 2 — reusing them)
# ============================================================

class ZoneAnalysis(BaseModel):
    status: str
    products_present: list[str]
    details: str

class ShelfAnalysis(BaseModel):
    compliance_score: int
    summary: str
    zones: dict[str, ZoneAnalysis]
    violations: list[str]
    positive_observations: list[str]
    recommendations: list[str]
    brands_detected: list[str]


# ============================================================
# SYSTEM PROMPT FOR CHAT
# ============================================================

SYSTEM_PROMPT = """
You are ShelfVision AI — an expert retail planogram compliance assistant 
with 10 years of experience in the FMCG and retail industry in Pakistan.

You have already analyzed a shelf image and have the full structured 
compliance report available as your context. 

Your behavior:
- Answer questions based ONLY on the shelf analysis provided
- Be specific, professional, and helpful
- Reference exact brands, zones, and scores from the analysis
- If asked for reports or summaries, format them professionally
- If asked something not related to the shelf analysis, politely 
  redirect back to the shelf compliance topic
- Remember everything discussed in the conversation so far
- When giving action items, be specific and prioritized

You are talking to a retail store manager who needs clear, 
actionable insights from the shelf audit.
"""


# ============================================================
# STEP 1: ANALYZE IMAGE (reusing Phase 2 logic)
# ============================================================

def analyze_shelf_image(image_path: str) -> ShelfAnalysis:
    """Runs Phase 2 structured analysis on the image"""

    print(f"📸 Analyzing shelf image: {image_path}")

    image = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or "JPEG")
    img_bytes = img_byte_arr.getvalue()

    analysis_prompt = """
    Analyze this retail shelf image and return a JSON object with EXACTLY this structure:
    {
      "compliance_score": <integer 0-100>,
      "summary": "<one sentence overall assessment>",
      "zones": {
        "eye_level": {
          "status": "<pass or fail>",
          "products_present": ["<brand1>", "<brand2>"],
          "details": "<detailed zone assessment>"
        },
        "golden_zone": {
          "status": "<pass or fail>",
          "products_present": ["<brand1>", "<brand2>"],
          "details": "<detailed zone assessment>"
        },
        "top_shelf": {
          "status": "<pass or fail>",
          "products_present": ["<brand1>", "<brand2>"],
          "details": "<detailed zone assessment>"
        },
        "bottom_shelf": {
          "status": "<pass or fail>",
          "products_present": ["<brand1>", "<brand2>"],
          "details": "<detailed zone assessment>"
        }
      },
      "violations": ["<violation 1>", "<violation 2>"],
      "positive_observations": ["<observation 1>", "<observation 2>"],
      "recommendations": ["<rec 1>", "<rec 2>", "<rec 3>"],
      "brands_detected": ["<brand1>", "<brand2>"]
    }
    Return ONLY this JSON. No other text.
    """

    response = google_client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="""You are a retail compliance analyst. 
            Always respond with valid JSON only. No markdown, no backticks.""",
            temperature=0.1
        ),
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            analysis_prompt
        ]
    )

    raw_text = response.text.strip()

    # Clean markdown fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    parsed = json.loads(raw_text)
    return ShelfAnalysis(**parsed)


# ============================================================
# STEP 2: BUILD CONTEXT STRING FROM ANALYSIS
# ============================================================

def build_context_from_analysis(analysis: ShelfAnalysis) -> str:
    """
    Converts structured analysis into a rich text context
    that gets injected into every conversation message.
    This is how the AI 'remembers' the shelf it analyzed.
    """

    zones_text = ""
    for zone_name, zone_data in analysis.zones.items():
        zones_text += f"""
  {zone_name.upper().replace('_', ' ')}:
    Status: {zone_data.status.upper()}
    Products: {', '.join(zone_data.products_present)}
    Details: {zone_data.details}
"""

    context = f"""
=== SHELF ANALYSIS REPORT (Already Completed) ===

COMPLIANCE SCORE: {analysis.compliance_score}/100
SUMMARY: {analysis.summary}

BRANDS DETECTED: {', '.join(analysis.brands_detected)}

ZONE ANALYSIS:
{zones_text}

VIOLATIONS FOUND ({len(analysis.violations)}):
{chr(10).join(f'- {v}' for v in analysis.violations) if analysis.violations else '- None'}

POSITIVE OBSERVATIONS:
{chr(10).join(f'- {o}' for o in analysis.positive_observations)}

TOP RECOMMENDATIONS:
{chr(10).join(f'{i+1}. {r}' for i, r in enumerate(analysis.recommendations))}

=== END OF ANALYSIS REPORT ===

You have full knowledge of this shelf. Answer manager questions based on this data.
"""
    return context


# ============================================================
# STEP 3: CHAT SESSION CLASS
# ============================================================

class ShelfChatSession:
    """
    Manages a full conversation session about a shelf image.
    Keeps track of all messages and automatically includes
    the shelf analysis context in every request.
    """

    def __init__(self, analysis: ShelfAnalysis):
        self.analysis = analysis
        self.context = build_context_from_analysis(analysis)

        # Initialize LangChain Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3,  # Slightly creative but mostly factual
        )

        # Chat history — starts with system message + context
        self.chat_history: list = [
            SystemMessage(content=SYSTEM_PROMPT + "\n\n" + self.context)
        ]

        print("\n✅ ShelfVision AI Chat Session Started!")
        print(f"📊 Shelf loaded: Score {analysis.compliance_score}/100")
        print(f"🏷️  Brands: {', '.join(analysis.brands_detected)}")
        print(f"⚠️  Violations: {len(analysis.violations)} found")

    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response.
        Full conversation history is maintained automatically.
        """

        # Add user message to history
        self.chat_history.append(HumanMessage(content=user_message))

        # Send full history to Gemini via LangChain
        response = self.llm.invoke(self.chat_history)

        # Add AI response to history
        self.chat_history.append(AIMessage(content=response.content))

        return response.content

    def get_history_summary(self) -> str:
        """Returns a summary of conversation turns so far"""
        turns = len([m for m in self.chat_history if isinstance(m, HumanMessage)])
        return f"{turns} questions asked in this session"

    def save_conversation(self, output_path: str):
        """Saves full conversation to a text file"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("SHELFVISION AI — CONVERSATION LOG\n")
            f.write("=" * 50 + "\n\n")
            for message in self.chat_history:
                if isinstance(message, HumanMessage):
                    f.write(f"MANAGER: {message.content}\n\n")
                elif isinstance(message, AIMessage):
                    f.write(f"SHELFVISION AI: {message.content}\n\n")
                    f.write("-" * 40 + "\n\n")
        print(f"\n💾 Conversation saved to {output_path}")


# ============================================================
# STEP 4: TERMINAL CHAT LOOP
# ============================================================

def run_chat_terminal(image_path: str):
    """
    Main function — analyzes image then starts
    an interactive terminal chat session.
    """

    print("\n" + "="*55)
    print("🏪  SHELFVISION AI — Retail Compliance Chat")
    print("="*55)

    # Phase 2: Analyze the image first
    print("\n⏳ Running shelf analysis...")
    analysis = analyze_shelf_image(image_path)
    print("✅ Analysis complete!\n")

    # Phase 3: Start chat session
    session = ShelfChatSession(analysis)

    print("\n" + "-"*55)
    print("💬 Chat started! Ask anything about this shelf.")
    print("   Type 'save' to save conversation log")
    print("   Type 'score' to see compliance score")
    print("   Type 'quit' to exit")
    print("-"*55 + "\n")

    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()

            # Skip empty input
            if not user_input:
                continue

            # Special commands
            if user_input.lower() == "quit":
                print("\n👋 Ending session...")
                session.save_conversation("logs/conversation_log.txt")
                break

            elif user_input.lower() == "save":
                session.save_conversation("logs/conversation_log.txt")
                continue

            elif user_input.lower() == "score":
                score = analysis.compliance_score
                icon = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                print(f"\n{icon} Current Score: {score}/100\n")
                continue

            # Normal chat message
            response = session.chat(user_input)
            print(f"\n🤖 ShelfVision AI: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted.")
            session.save_conversation("logs/conversation_log.txt")
            break


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    IMAGE_PATH = "images/test_shelf.jpg"

    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Image not found at: {IMAGE_PATH}")
    else:
        run_chat_terminal(IMAGE_PATH)