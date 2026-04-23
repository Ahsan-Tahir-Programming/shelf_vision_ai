# app/core/analyzer.py
import google.genai as genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
from app.models.schemas import ShelfAnalysis
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
import os
import io
import json

load_dotenv()

# Single client instance — reused across the app
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = GEMINI_MODEL

ANALYSIS_SYSTEM_PROMPT = """You are a retail compliance analyst. 
Always respond with valid JSON only. No markdown, no backticks."""

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
  "violations": ["<violation 1>"],
  "positive_observations": ["<observation 1>"],
  "recommendations": ["<rec 1>", "<rec 2>", "<rec 3>"],
  "brands_detected": ["<brand1>", "<brand2>"]
}
Return ONLY this JSON. No other text.
"""


def analyze_shelf_image(image_path: str) -> ShelfAnalysis:
    """
    Analyzes a shelf image and returns a validated ShelfAnalysis object.
    This is the single source of truth for image analysis in the app.
    """

    image = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or "JPEG")
    img_bytes = img_byte_arr.getvalue()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=ANALYSIS_SYSTEM_PROMPT,
            temperature=0.1
        ),
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            ANALYSIS_PROMPT
        ]
    )

    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    parsed = json.loads(raw_text)
    return ShelfAnalysis(**parsed)