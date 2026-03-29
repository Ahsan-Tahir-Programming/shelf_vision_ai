from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
import os
import io

# Load API key from .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- SYSTEM PROMPT ----
SYSTEM_PROMPT = """
You are an expert retail planogram compliance analyst with 10 years of experience 
in the FMCG and retail industry. 

When analyzing shelf images, you focus on:
- Product placement (eye-level, golden zone, top/bottom shelf)
- Brand blocking (same brand products grouped together)
- Facing count (how many product faces are visible)
- Empty spaces or gaps on shelves
- Overall shelf organization and compliance

Always be specific, professional, and actionable in your analysis.
"""

# ---- ANALYSIS FUNCTION ----
def analyze_shelf_image(image_path: str) -> str:
    """
    Takes a shelf image path, sends it to Gemini Vision,
    and returns a compliance analysis report.
    """

    print(f"\n📸 Loading image: {image_path}")

    # Load image and convert to bytes
    image = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or "JPEG")
    img_bytes = img_byte_arr.getvalue()

    print("🤖 Sending to Gemini for analysis...")
    print("-" * 50)

    # Analysis prompt
    analysis_prompt = """
    Please analyze this retail shelf image and provide:
    
    1. OVERALL COMPLIANCE SCORE (0-100)
    2. SHELF ZONES ANALYSIS
       - Eye Level Zone (most important): What products are here? Compliant?
       - Golden Zone (waist to eye level): Assessment
       - Top Shelf: Assessment
       - Bottom Shelf: Assessment
    3. VIOLATIONS FOUND (list each one clearly)
    4. POSITIVE OBSERVATIONS (what is done well)
    5. TOP 3 RECOMMENDATIONS (what to fix first, in priority order)
    
    Be specific about product positions and brand placement.
    """

    # Send to Gemini using new SDK
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=[
            types.Part.from_bytes(
                data=img_bytes,
                mime_type="image/jpeg"
            ),
            analysis_prompt
        ]
    )

    return response.text

# ---- MAIN EXECUTION ----
if __name__ == "__main__":

    IMAGE_PATH = "images/test_shelf.jpg"

    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Image not found at: {IMAGE_PATH}")
        print("👉 Please add a shelf image to the images/ folder")
    else:
        result = analyze_shelf_image(IMAGE_PATH)

        print("\n📊 SHELF COMPLIANCE ANALYSIS REPORT")
        print("=" * 50)
        print(result)
        print("=" * 50)

        # Save report
        with open("logs/analysis_report.txt", "w", encoding="utf-8") as f:
            f.write(result)

        print("\n✅ Report saved to logs/analysis_report.txt")
        