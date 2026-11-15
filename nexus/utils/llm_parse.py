# -*- coding: utf-8 -*-
"""Robust parsing of Gemini output. Never turns an API failure into 'Not a Resume'."""
import json, re

def is_api_error(raw) -> bool:
    return (not raw) or (not raw.strip()) or raw.lstrip().startswith("⚠️")

def extract_json(raw):
    s = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", raw.strip())
    i = s.find("{")
    if i < 0: return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(s[i:])
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None

def to_int(v, default=None, lo=0, hi=100):
    m = re.search(r"-?\d+(?:\.\d+)?", str(v)) if v is not None else None
    return max(lo, min(hi, int(float(m.group())))) if m else default

def parse_evaluation(raw: str) -> dict:
    """status: 'ok' | 'partial' (JSON cut off, score recovered) | 'error' (retry / show 'AI unavailable')."""
    if is_api_error(raw):
        return {"status": "error", "ats_score": None, "summary": (raw or "Empty response from AI.")[:200]}
    d = extract_json(raw)
    if d is not None:
        d["ats_score"] = to_int(d.get("ats_score"), default=None)
        d["status"] = "ok" if d["ats_score"] is not None or d.get("is_valid_resume") is False else "error"
        if d.get("is_valid_resume") is False:
            d["ats_score"], d["verdict"] = 0, "Rejected - Not a Resume"
        return d
    m = re.search(r'"ats_score"\s*:\s*"?(\d+)', raw)
    if m:
        return {"status": "partial", "ats_score": to_int(m.group(1)), "strengths": [], "red_flags": [],
                "missing_keywords": [], "key_improvements": [], "summary": "AI output was cut off; only the score was recovered."}
    return {"status": "error", "ats_score": None, "summary": "AI returned unreadable output."}
