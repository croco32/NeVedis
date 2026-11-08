"""NeVedis analysis pipeline: rules -> Gemini (JSON + schema) -> final score and verdict.

    final = 0.6 * gemini_score + 0.4 * rule_score
    any hard red flag (rules or Gemini) -> final >= 80
    verdict from final: 70-100 high, 40-69 medium, 0-39 low
    AI score alone when the rules have nothing to say: screenshot/audio only (they can't see it),
    or no rule signal at all (story-only scams like "Mom, new number" have no keywords to count)
If Gemini fails twice, times out, or errors, the result falls back to the rules alone.
"""
import concurrent.futures as cf
import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

import rules
import scams
from config import BACKUP_MODELS, MODEL

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")

TIMEOUT_S = 60
PROMPT_TEMPLATE = (HERE / "nevedis_prompt.md").read_text().split("\n---\n", 1)[1].strip()
SCHEMA = json.loads((HERE / "nevedis_schema.json").read_text())
HARD_FLAG_IDS = set(SCHEMA["properties"]["hard_red_flags"]["items"]["enum"])
LOW_MESSAGE = "No strong red flags found. Still verify through the official phone number or app."

CHANNELS = {"SMS": "sms", "Email": "email", "Phone call": "phone_call", "Messenger": "messenger", "Unknown": "unknown"}
AUDIO_MIME = {"mp3": "audio/mp3", "wav": "audio/wav", "m4a": "audio/mp4"}
IMAGE_MIME = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}

_POOL = cf.ThreadPoolExecutor(max_workers=4)


class GeminiUnavailable(Exception):
    """Raised with a friendly, user-facing message."""


# ---------- fix #1: neutralize anything that could close or reopen the <item> fence ----------
_FENCE = re.compile(r"<\s*(/?)\s*item\b[^>]*>", re.I)


def defang(text: str) -> str:
    return _FENCE.sub(lambda m: "[/item]" if m.group(1) else "[item]", text or "")


def build_system_prompt(message: str, rule_result: dict, channel: str, attachments: list[str]) -> str:
    values = {
        "rule_signals": defang(rules.format_for_prompt(rule_result)),
        "channel": CHANNELS.get(channel, "unknown"),
        "scam_families": scams.prompt_list(),
        "attachments": "; ".join(attachments) if attachments else "none",
        "message": defang(message.strip()) or "(no text: the item is in the attached file)",
    }
    # Single pass, so text inside the message can never trigger another placeholder.
    return re.sub(r"\{(rule_signals|channel|scam_families|attachments|message)\}", lambda m: values[m.group(1)], PROMPT_TEMPLATE)


# ---------- Gemini ----------
def _client():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise GeminiUnavailable("No Gemini API key is set, so this check used NeVedis's built-in rules only.")
    return genai.Client(api_key=key, http_options=types.HttpOptions(timeout=TIMEOUT_S * 1000))


def _valid(d) -> bool:
    try:
        return (isinstance(d, dict) and all(k in d for k in SCHEMA["required"])
                and isinstance(d["risk_score"], int) and 0 <= d["risk_score"] <= 100
                and isinstance(d["red_flags"], list) and isinstance(d["what_to_do"], list)
                and all(k in d["three_p"] for k in ("pretext", "pressure", "payoff_ask")))
    except Exception:
        return False


def _ask_gemini(system_prompt: str, files: list[tuple[bytes, str]]) -> dict:
    client = _client()
    parts = [types.Part.from_bytes(data=b, mime_type=mt) for b, mt in files]
    parts.append(types.Part.from_text(text="Analyze the item described in your instructions and return the JSON."))
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_json_schema=SCHEMA,
        temperature=0.2,
        thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
    )
    contents = [types.Content(role="user", parts=parts)]
    last_err = None
    # Main model first; if it is missing, out of quota or busy, move straight to the next model.
    for model in [MODEL, *[m for m in BACKUP_MODELS if m != MODEL]]:
        try:
            for attempt in (1, 2):  # retry once if the answer is not valid JSON for the schema
                r = client.models.generate_content(model=model, contents=contents, config=config)
                try:
                    data = json.loads(r.text or "")
                    if _valid(data):
                        data["_model"] = model
                        return data
                except json.JSONDecodeError:
                    pass
            raise GeminiUnavailable("The AI gave an unreadable answer twice, so this check used NeVedis's built-in rules only.")
        except errors.APIError as e:
            if e.code in (404, 429, 500, 503):  # missing, out of quota, or busy: try the next model
                last_err = e
                continue
            raise
    raise last_err


def _friendly(e: Exception) -> str:
    if isinstance(e, GeminiUnavailable):
        return str(e)
    if isinstance(e, (cf.TimeoutError, TimeoutError)) or "timed out" in str(e).lower() or "timeout" in type(e).__name__.lower():
        return f"The AI check took longer than {TIMEOUT_S} seconds, so this result uses NeVedis's built-in rules only. Try again in a minute for a full check."
    if isinstance(e, errors.APIError):
        if e.code in (400, 401, 403) and "key" in str(e).lower():
            return "The Gemini API key was rejected, so this check used NeVedis's built-in rules only."
        if e.code == 429 and "perday" in str(e).lower().replace(" ", ""):
            return "Today's free AI checks are used up (Google's free plan allows a limited number per day). They reset tomorrow."
        if e.code in (429, 500, 503, 504):
            return "The AI is busy right now (Google reports high demand). Try again in a minute."
        if e.code == 400 and ("mime" in str(e).lower() or "unsupported" in str(e).lower()):
            return "The AI couldn't read that file type, so this check used NeVedis's built-in rules only."
    return "The AI check is not available right now."


# ---------- scoring ----------
def verdict_for(score: int) -> str:
    return "high" if score >= 70 else "medium" if score >= 40 else "low"


def combine(gemini_score, rule_score: int, hard: bool, has_text: bool = True, rule_signals: int = 0) -> int:
    if gemini_score is None:
        final = rule_score
    elif not has_text or rule_signals == 0:
        final = gemini_score  # rules can't read screenshots/audio, or found nothing to weigh
    else:
        final = round(0.6 * gemini_score + 0.4 * rule_score)
    return max(final, 80) if hard else final


_SAFE_CLAIM = re.compile(r"\b(is|are|looks?|seems?|appears?( to be)?|probably|likely|completely|totally|perfectly)\s+safe\b", re.I)
_SAFE = re.compile(r"\bsafe(ly)?\b", re.I)


def no_safe(text: str) -> str:
    """Never let generated text call something 'safe' (quotes from the item are left untouched)."""
    text = _SAFE_CLAIM.sub("shows no strong red flags", text or "")
    return _SAFE.sub(lambda m: ("Securely" if m.group(1) else "Secure") if m.group(0)[0].isupper() else ("securely" if m.group(1) else "secure"), text)


def _scrub(d: dict) -> dict:
    d["summary"] = no_safe(d.get("summary", ""))
    d["next_move"] = no_safe(d.get("next_move", ""))
    d["share_warning"] = no_safe(d.get("share_warning", ""))
    d["what_to_do"] = [no_safe(x) for x in d.get("what_to_do", [])]
    for f in d.get("red_flags", []):
        f["explanation"] = no_safe(f.get("explanation", ""))
    for k in ("pretext", "pressure", "payoff_ask"):
        p = d["three_p"].get(k, {})
        if "claimed_identity" in p:
            p["claimed_identity"] = no_safe(p["claimed_identity"])
    return d


def _fallback_advice(verdict: str, signals: list[dict]) -> tuple[str, list[str]]:
    ids = {s["id"] for s in signals}
    if verdict == "high":
        summary = "This message has strong signs of a scam."
    elif verdict == "medium":
        summary = "This message has some warning signs. Be careful."
    else:
        summary = LOW_MESSAGE
    steps = []
    if verdict != "low":
        steps.append("Do not click links, reply, or call numbers in the message.")
    if ids & {"unusual_payment_method", "government_payment_threat"}:
        steps.append("Do not pay. Real agencies and companies never ask for gift cards, crypto, wires, Zelle or Cash App.")
    if "asks_for_code_or_password" in ids:
        steps.append("Never share a code or password, even with someone who says they are from your bank.")
    if "remote_access_request" in ids:
        steps.append("Do not install any app they name. If you already did, turn off the internet and ask a trusted person for help.")
    steps.append("Check by calling the official number on your card, bill, or the company's real website or app.")
    return summary, steps[:4]


# ---------- main entry point ----------
def analyze(text: str, channel: str = "Unknown", image: tuple[bytes, str] | None = None, audio: tuple[bytes, str] | None = None) -> dict:
    """image/audio: (bytes, file extension). Returns everything the result card needs."""
    t0 = time.monotonic()
    rule_result = rules.check(text)
    files, attachments = [], []
    if image:
        files.append((image[0], IMAGE_MIME[image[1]])); attachments.append(f"1 screenshot ({IMAGE_MIME[image[1]]})")
    if audio:
        files.append((audio[0], AUDIO_MIME[audio[1]])); attachments.append(f"1 audio recording ({AUDIO_MIME[audio[1]]})")
    system_prompt = build_system_prompt(text, rule_result, channel, attachments)

    gemini, notice = None, None
    try:
        gemini = _POOL.submit(_ask_gemini, system_prompt, files).result(timeout=TIMEOUT_S)  # fix: hard 60 s cap overall
        gemini = _scrub(gemini)
    except Exception as e:  # noqa: BLE001 - every failure becomes a friendly rules-only result
        notice = _friendly(e)

    used_model = gemini.pop("_model", MODEL) if gemini else MODEL
    rule_hard = [s for s in rule_result["signals"] if s["kind"] == "hard"]
    gem_hard = [f for f in (gemini or {}).get("hard_red_flags", []) if f in HARD_FLAG_IDS]
    hard = bool(rule_hard or gem_hard)
    # Without the AI we can't judge pictures, audio, or a story with no keywords. Never show a calm
    # "low" result we can't stand behind: only trust rules-only when they found real red flags.
    if not gemini and combine(None, rule_result["rule_score"], hard) < 40:
        why = ("NeVedis can't read screenshots or recordings without the AI." if not text.strip()
               else "Our instant checks found no red flags, but they can't judge the story itself.")
        return {"final_score": None, "verdict": "unknown", "gemini_score": None, "rule_score": rule_result["rule_score"],
                "hard": hard, "hard_ids": [], "category": None, "scam_type": None, "three_p": None,
                "summary": f"{why} Please try again soon. Until then, don't reply, click, or pay, and check with the company's official number.",
                "what_to_do": ["Don't reply, click links, or pay anything yet.", "Call the company or person using a number you already know, not one in the message.", "Try NeVedis again in a little while."],
                "red_flags": [], "rule_signals": rule_result["signals"], "links": rule_result["links"], "family": None,
                "next_move": "", "share_warning": "", "notice": notice, "seconds": round(time.monotonic() - t0, 1), "model": MODEL}
    final = combine(gemini["risk_score"] if gemini else None, rule_result["rule_score"], hard, bool(text.strip()), len(rule_result["signals"]))
    verdict = verdict_for(final)

    if gemini:
        summary, steps = gemini["summary"], gemini["what_to_do"]
        family_id = gemini.get("scam_type")
        next_move, share = gemini.get("next_move", ""), gemini.get("share_warning", "")
        if verdict == "low":
            summary = f"{summary} {LOW_MESSAGE}" if summary else LOW_MESSAGE
    else:
        summary, steps = _fallback_advice(verdict, rule_result["signals"])
        family_id = scams.guess_family(text) if verdict != "low" else None
        fam = scams.BY_ID.get(family_id or "")
        next_move = f"If you reply, the usual next step is: {fam['steps'][2].lower()}." if fam else ""
        share = f"Heads up: I got a message that looks like a \"{fam['name']}\" scam. {fam['tell']}" if fam else ""
    family = scams.public_family(family_id) if verdict != "low" or (gemini and gemini.get("category") in ("scam", "phishing")) else None

    return {
        "final_score": final, "verdict": verdict, "gemini_score": gemini["risk_score"] if gemini else None,
        "rule_score": rule_result["rule_score"], "hard": hard, "hard_ids": sorted({s["id"] for s in rule_hard} | set(gem_hard)),
        "category": (gemini or {}).get("category"), "scam_type": (gemini or {}).get("scam_type"),
        "summary": summary, "what_to_do": steps, "three_p": (gemini or {}).get("three_p"),
        "red_flags": (gemini or {}).get("red_flags", []), "rule_signals": rule_result["signals"],
        "links": rule_result["links"], "family": family, "next_move": next_move, "share_warning": share,
        "notice": notice, "seconds": round(time.monotonic() - t0, 1), "model": used_model,
    }
