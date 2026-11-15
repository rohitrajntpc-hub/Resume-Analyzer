# -*- coding: utf-8 -*-
"""Fixed resume_parser.py: tiered validator + real PII masking. Drop-in replacement (same function names/returns)."""
import re

STRONG = [r"\bexperience\b", r"\beducation\b", r"\bskills\b", r"\bprojects?\b", r"\bwork\s+history\b",
          r"\bemployment\b", r"\bcurriculum\s+vitae\b", r"\bresume\b", r"\bcertificat(e|ion)s?\b",
          r"\bobjective\b", r"\bprofessional\s+summary\b", r"\binternships?\b", r"\bachievements?\b",
          r"\bqualifications?\b"]
EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
PHONE = r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?(?:\d{5}[\s.-]?\d{5}|\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})(?!\d)"
DATE_RANGE = r"(19|20)\d{2}\s*(?:-|–|—|\bto\b)\s*((19|20)\d{2}|present|current|ongoing)"
DEGREE = r"\b(b\.?\s?tech|m\.?\s?tech|bca|mca|b\.?sc|m\.?sc|mba|bba|b\.?com|m\.?com|bachelor|master|ph\.?d|diploma|cgpa)\b"
# phrases that mean "this is clearly something else"
NON_RESUME = ["job description", "we are hiring", "we are looking for", "to apply", "apply now", "dear hiring manager",
              "dear sir", "dear madam", "terms and conditions", "account summary", "units consumed", "ingredients",
              "pnr", "invitation", "syllabus", "meeting notes", "action items", "abstract:", "research abstract",
              "about us", "amount payable", "due date", "invoice", "transactions", "def ", "import ", "tenant",
              "landlord", "agreement", "terms of use", "privacy policy", "breaking:", "question paper", "marks:"]

def extract_text_from_pdf(uploaded_file) -> str:
    import pypdf  # lazy import so the validator can be tested without pypdf
    try:
        reader = pypdf.PdfReader(uploaded_file)
        return "\n".join((p.extract_text() or "") for p in reader.pages).strip()
    except Exception:
        return ""

def validate_resume(text: str) -> tuple[bool, str]:
    """Tiered: hard-reject known non-resumes -> accept on strong signals -> 'uncertain' goes to the AI's is_valid_resume check."""
    if not text or len(text.strip()) < 80:
        return False, "File contains insufficient or no readable text."
    t = text.lower()
    for m in NON_RESUME:
        if m in t:
            return False, f"Looks like a non-resume document (found '{m.strip()}')."
    strong = sum(1 for p in STRONG if re.search(p, t))
    career = sum(bool(re.search(p, t)) for p in (DATE_RANGE, DEGREE))      # dates / degree = career evidence
    contact = sum(bool(re.search(p, text)) for p in (EMAIL, PHONE))        # contact alone proves nothing
    if strong >= 2 or (strong >= 1 and career + contact >= 1) or career >= 2 or (career >= 1 and contact >= 1):
        return True, "Valid Resume"
    list_commas = max((l.count(",") for l in text.splitlines()), default=0)   # skills-style list
    if len(text.strip()) >= 150 and list_commas >= 3 and career >= 1:
        return True, "Uncertain - AI will verify"
    if len(text.strip()) >= 200 and list_commas >= 4:
        return True, "Uncertain - AI will verify"
    return False, "Does not look like a Resume/CV (no experience, education, skills, dates or contact info found)."

def mask_candidate_pii(text: str) -> tuple[str, dict]:
    """Masks email, phone, profile links, institution names, honorifics/pronouns and the candidate's NAME."""
    extracted = {"email": "", "phone": "", "name": ""}
    m = re.search(EMAIL, text)
    if m: extracted["email"] = m.group(0)
    p = re.search(PHONE, text)
    if p: extracted["phone"] = p.group(0).strip()

    # name = first non-empty line, first chunk before | - , :
    first = next((l.strip() for l in text.splitlines() if l.strip()), "")
    chunk = re.split(r"\s*[|•·,:]\s*|\s+[-–—]\s+", first)[0]
    name_tokens = [w for w in re.findall(r"[A-Za-z][A-Za-z'.]+", chunk) if len(w) > 2]
    if 1 <= len(name_tokens) <= 4: extracted["name"] = " ".join(name_tokens)
    else: name_tokens = []

    t = re.sub(EMAIL, "[EMAIL REDACTED]", text)
    t = re.sub(PHONE, "[PHONE REDACTED]", t)
    t = re.sub(r"(?i)\b(?:https?://)?(?:www\.)?(?:linkedin|github|gitlab|behance|twitter|x)\.com/[^\s|,;]+", "[LINK REDACTED]", t)
    inst = (r"(?:[A-Z][\w'’.&-]*[ \t]+){0,4}(?:Institute|University|College|Academy|School)\b"
            r"(?:[ \t]+of[ \t]+[A-Z]\w+(?:[ \t]+[A-Z]\w+)?)?|\b(?:IIT|NIT|IIIT|BITS|IISc|NSIT|DTU|IIM|KIIT|NMIMS|VIT|SRM|MIT|XLRI|ISB|JNU|BHU|AMU|SPPU|IGNOU|MNNIT|NITK|COEP|VJTI|PICT|LNMIIT|IISER|JMI)\b(?:[ \t]+[A-Z][a-z]+)?")
    t = re.sub(inst, "[INSTITUTION REDACTED]", t)
    for tok in name_tokens:
        t = re.sub(rf"(?i)\b{re.escape(tok)}\b", "[CANDIDATE]", t)
    t = re.sub(r"(?i)\b(he|she|him|her|his|hers)\b|\b(mr|ms|mrs)\.", "[INDIVIDUAL]", t)
    return t, extracted
