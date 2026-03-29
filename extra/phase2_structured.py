from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import io
import json

# Load API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================================
# PYDANTIC MODELS — Define the exact shape of your data
# ============================================================

class ZoneAnalysis(BaseModel):
    """Analysis for a single shelf zone"""
    status: str = Field(description="pass or fail")
    products_present: list[str] = Field(description="List of products/brands found here")
    details: str = Field(description="Detailed assessment of this zone")

class ShelfAnalysis(BaseModel):
    """Complete structured analysis of a shelf image"""
    compliance_score: int = Field(description="Overall score from 0 to 100")
    summary: str = Field(description="One sentence summary of overall shelf condition")
    zones: dict[str, ZoneAnalysis] = Field(
        description="Analysis per zone: eye_level, golden_zone, top_shelf, bottom_shelf"
    )
    violations: list[str] = Field(description="List of specific violations found")
    positive_observations: list[str] = Field(description="List of things done well")
    recommendations: list[str] = Field(description="Top 3 prioritized recommendations")
    brands_detected: list[str] = Field(description="All brand names detected on shelf")


# ============================================================
# SYSTEM PROMPT — Now instructs JSON output
# ============================================================

SYSTEM_PROMPT = """
You are an expert retail planogram compliance analyst with 10 years of experience 
in the FMCG and retail industry.

CRITICAL INSTRUCTION: You must ALWAYS respond with valid JSON only.
- No markdown, no backticks, no explanation text outside the JSON
- No ```json fences
- Just raw, valid JSON that matches the requested structure exactly
- All field names must match exactly as specified

When analyzing shelf images, focus on:
- Product placement (eye-level, golden zone, top/bottom shelf)
- Brand blocking (same brand products grouped together)
- Facing count (how many product faces are visible)
- Empty spaces or gaps on shelves
- Overall shelf organization and compliance
"""


# ============================================================
# ANALYSIS PROMPT — Tells Gemini exact JSON structure to return
# ============================================================

ANALYSIS_PROMPT = """
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
  "violations": [
    "<specific violation 1>",
    "<specific violation 2>"
  ],
  "positive_observations": [
    "<positive point 1>",
    "<positive point 2>"
  ],
  "recommendations": [
    "<priority 1 recommendation>",
    "<priority 2 recommendation>",
    "<priority 3 recommendation>"
  ],
  "brands_detected": ["<brand1>", "<brand2>", "<brand3>"]
}

Return ONLY this JSON. No other text.
"""


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_shelf_structured(image_path: str) -> ShelfAnalysis:
    """
    Analyzes a shelf image and returns a validated Pydantic object.
    Raises clear errors if something goes wrong.
    """

    print(f"\n📸 Loading image: {image_path}")
    image = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or "JPEG")
    img_bytes = img_byte_arr.getvalue()

    print("🤖 Sending to Gemini for structured analysis...")
    print("-" * 50)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1  # Low temperature = more consistent, predictable output
        ),
        contents=[
            types.Part.from_bytes(
                data=img_bytes,
                mime_type="image/jpeg"
            ),
            ANALYSIS_PROMPT
        ]
    )

    raw_text = response.text.strip()

    # ---- Parse JSON safely ----
    try:
        # Clean any accidental markdown fences if Gemini adds them
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        
        parsed_json = json.loads(raw_text)

    except json.JSONDecodeError as e:
        print(f"\n❌ Gemini returned invalid JSON: {e}")
        print(f"Raw response was:\n{raw_text}")
        raise

    # ---- Validate with Pydantic ----
    try:
        analysis = ShelfAnalysis(**parsed_json)
    except Exception as e:
        print(f"\n❌ JSON structure doesn't match expected schema: {e}")
        raise

    return analysis


# ============================================================
# DISPLAY FUNCTION — Pretty print the structured result
# ============================================================

def display_analysis(analysis: ShelfAnalysis):
    """Displays the structured analysis in a readable format"""

    print(f"\n{'='*55}")
    print(f"📊  SHELF COMPLIANCE REPORT")
    print(f"{'='*55}")

    # Score with visual indicator
    score = analysis.compliance_score
    if score >= 80:
        indicator = "🟢 EXCELLENT"
    elif score >= 60:
        indicator = "🟡 NEEDS IMPROVEMENT"
    else:
        indicator = "🔴 CRITICAL"

    print(f"\n🏆 COMPLIANCE SCORE: {score}/100  {indicator}")
    print(f"📝 SUMMARY: {analysis.summary}")

    # Brands detected
    print(f"\n🏷️  BRANDS DETECTED: {', '.join(analysis.brands_detected)}")

    # Zone analysis
    print(f"\n📍 ZONE ANALYSIS:")
    zone_labels = {
        "eye_level": "👁️  Eye Level",
        "golden_zone": "⭐ Golden Zone",
        "top_shelf": "⬆️  Top Shelf",
        "bottom_shelf": "⬇️  Bottom Shelf"
    }
    for zone_key, zone_data in analysis.zones.items():
        label = zone_labels.get(zone_key, zone_key)
        status_icon = "✅" if zone_data.status == "pass" else "❌"
        print(f"\n  {label}: {status_icon} {zone_data.status.upper()}")
        print(f"  Products: {', '.join(zone_data.products_present)}")
        print(f"  Details: {zone_data.details}")

    # Violations
    print(f"\n⚠️  VIOLATIONS ({len(analysis.violations)} found):")
    if analysis.violations:
        for i, v in enumerate(analysis.violations, 1):
            print(f"  {i}. {v}")
    else:
        print("  None — Perfect compliance!")

    # Positive observations
    print(f"\n✅ POSITIVE OBSERVATIONS:")
    for i, obs in enumerate(analysis.positive_observations, 1):
        print(f"  {i}. {obs}")

    # Recommendations
    print(f"\n🎯 TOP RECOMMENDATIONS:")
    for i, rec in enumerate(analysis.recommendations, 1):
        print(f"  {i}. {rec}")

    print(f"\n{'='*55}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    IMAGE_PATH = "images/test_shelf.jpg"

    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Image not found at: {IMAGE_PATH}")
    else:
        # Get structured analysis
        analysis = analyze_shelf_structured(IMAGE_PATH)

        # Display it nicely
        display_analysis(analysis)

        # Save as clean JSON file
        output_path = "logs/structured_analysis.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis.model_dump(), f, indent=2)

        print(f"\n✅ Structured JSON saved to {output_path}")
        print("\n🔍 Raw JSON preview:")
        print(json.dumps(analysis.model_dump(), indent=2)[:500] + "...")