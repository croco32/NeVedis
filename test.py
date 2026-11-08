"""Quick check that your Gemini API key works with NeVedis.

Run:  .venv/bin/python test.py

Test 1: a plain request (is the key valid, is the model available?)
Test 2: a JSON request using nevedis_schema.json (does Gemini accept our schema?)
"""
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from config import MODEL

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")
KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not KEY:
    sys.exit("No key yet. Open .env and paste it after GEMINI_API_KEY= (no quotes, no spaces), then run this again.")

client = genai.Client(api_key=KEY)


def explain(e: errors.APIError) -> str:
    if e.code in (400, 401, 403) and "key" in str(e).lower():
        return "Google rejected the API key. Copy it again from https://aistudio.google.com/apikey and paste it into .env."
    if e.code == 404:
        return f"Model '{MODEL}' was not found for this key. Change MODEL in config.py."
    if e.code == 429:
        return "Rate limit or quota reached. Wait a minute and try again."
    return f"Gemini error {e.code}: {e.message}"


try:
    print(f"Model: {MODEL}")
    print("Test 1: plain request ...", end=" ", flush=True)
    r = client.models.generate_content(model=MODEL, contents="Reply with exactly: NeVedis key works")
    print("OK ->", (r.text or "").strip())

    print("Test 2: JSON schema request ...", end=" ", flush=True)
    schema = json.loads((HERE / "nevedis_schema.json").read_text())
    r = client.models.generate_content(
        model=MODEL,
        contents="Analyze this SMS and answer in English: 'USPS: Your package is on hold. Pay $1.99 at usps-redelivery-help.com within 24 hours.'",
        config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=schema),
    )
    data = json.loads(r.text)
    print(f"OK -> category={data['category']}, risk_score={data['risk_score']}")
    print("\nYour API key works. NeVedis is ready to build.")
except errors.APIError as e:
    sys.exit("\nFAILED: " + explain(e))
except json.JSONDecodeError:
    sys.exit("\nFAILED: Gemini answered, but not with valid JSON for the schema.")
except Exception as e:  # network problems, etc.
    sys.exit(f"\nFAILED: {type(e).__name__}: {e}")
