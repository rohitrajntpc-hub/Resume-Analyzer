# -*- coding: utf-8 -*-
import os
import json
import re
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

ACTIVE_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-pro-latest"
]

_configured = False

def configure_gemini():
    global _configured
    if _configured:
        return True
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    _configured = True
    return True

# Turbo fast config with strictly limited tokens to ensure < 1.0s response per resume
TURBO_GEN_CONFIG = {
    "temperature": 0.1,
    "max_output_tokens": 800,
    "top_p": 0.8
}

def query_gemini(prompt: str, system_prompt: str = "You are an elite, strict ATS Auditor and Hiring Director.") -> str:
    """Queries Gemini with working models and automatic failover."""
    if not configure_gemini():
        return "⚠️ Error: GEMINI_API_KEY is not configured in backend .env."

    last_error = ""
    for model_name in ACTIVE_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt,
                generation_config=TURBO_GEN_CONFIG
            )
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            time.sleep(0.3)
            continue

    return f"⚠️ API Error: {last_error}"

def evaluate_resume_structured(resume_text: str, target_jd: str = "") -> dict:
    """
    Evaluates a resume strictly against target JD or rigorous industry criteria.
    Includes built-in validation to reject non-resume inputs with 0 score.
    NEVER hardcodes 70 or default score on real resumes.
    """
    if not configure_gemini():
        return {
            "is_valid_resume": False,
            "candidate_name": "Unknown",
            "ats_score": 0,
            "verdict": "Configuration Error",
            "match_percentage": "0%",
            "summary": "GEMINI_API_KEY is missing in backend .env.",
            "strengths": [],
            "red_flags": ["API Key missing"],
            "missing_keywords": [],
            "key_improvements": []
        }

    trimmed_resume = resume_text[:3500]
    trimmed_jd = target_jd[:1500] if target_jd else "General Software/Data/Tech Industry Engineering Standards"

    prompt = f"""You are a strict ATS Auditor and Technical Hiring Committee Lead.

Carefully evaluate the following candidate document against the provided Job Description.

FIRST CHECK: Is this truly a professional Resume or CV of a person?
If the text is a recipe, book chapter, receipt, invoice, random notes, code snippet, assignment, or non-resume content, set "is_valid_resume": false and "ats_score": 0.

DOCUMENT TO EVALUATE:
\"\"\"
{trimmed_resume}
\"\"\"

TARGET JOB DESCRIPTION:
\"\"\"
{trimmed_jd}
\"\"\"

SCORING CRITERIA:
- Evaluate dynamically based on true relevance between the candidate's skills and the JD.
- 85-100: Exceptional match with high-impact quantifiable metrics, exact tech stack, strong projects & experience.
- 70-84: Solid background, meets primary requirements, minor gaps in metrics or specialized tools.
- 50-69: Partially qualified, lacks depth, relevant tech keywords or quantifiable achievements.
- 20-49: Poor match, irrelevant domain, or heavily deficient qualifications.
- 0: INVALID DOCUMENT / NOT A RESUME.

Return ONLY a valid raw JSON object (NO markdown fences, no triple backticks, no comments) matching this exact schema:
{{
  "is_valid_resume": true,
  "candidate_name": "Extracted Full Name from the document",
  "ats_score": 78,
  "verdict": "Strong Match" or "Potential Match" or "Needs Improvement" or "Rejected - Not a Resume",
  "match_percentage": "78%",
  "summary": "Concise, truthful executive recruiter assessment explaining the exact rationale for this score.",
  "strengths": [
    "Specific technical or architectural highlight 1",
    "Specific metric or project highlight 2"
  ],
  "red_flags": [
    "Specific gap or weak bullet 1",
    "Specific missing qualification or vagueness 2"
  ],
  "missing_keywords": [
    "Keyword1",
    "Keyword2",
    "Keyword3"
  ],
  "key_improvements": [
    {{"before": "Verbatim weak bullet from document", "after": "High-impact rewrite using Google X-Y-Z formula"}}
  ]
}}"""

    raw_response = query_gemini(prompt)

    # Clean JSON format
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        data["ats_score"] = int(data.get("ats_score", 0))
        if not data.get("is_valid_resume", True):
            data["ats_score"] = 0
            data["verdict"] = "Rejected - Not a Resume"
        return data
    except Exception:
        # Fallback regex extraction from AI text
        score_match = re.search(r'"ats_score"\s*:\s*(\d+)', raw_response)
        score = int(score_match.group(1)) if score_match else 0
        is_valid = False if score == 0 or "not a resume" in raw_response.lower() else True

        name_match = re.search(r'"candidate_name"\s*:\s*"([^"]+)"', raw_response)
        name = name_match.group(1) if name_match else "Applicant"

        return {
            "is_valid_resume": is_valid,
            "candidate_name": name,
            "ats_score": score,
            "verdict": "Evaluated" if is_valid else "Rejected - Not a Resume",
            "match_percentage": f"{score}%",
            "summary": raw_response[:300] if is_valid else "The uploaded file does not contain a valid resume.",
            "strengths": ["Document parsed"],
            "red_flags": ["Please review file format"],
            "missing_keywords": [],
            "key_improvements": []
        }
