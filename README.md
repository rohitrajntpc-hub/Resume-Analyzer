# 💠 NexusATS — AI Resume Screening & Career Toolkit

A Streamlit app that screens resumes with Google Gemini, matches candidates across multiple job openings, and helps job seekers improve their resumes. It combines a rule-based pre-validator, optional PII redaction for blind screening, structured-JSON LLM scoring, and a keyword-based fallback when the LLM is unavailable.

> ⚠️ **Decision support only.** LLM scores are non-deterministic. Use this tool to prioritise reading, not to make final hiring decisions. Automated candidate scoring is regulated in some jurisdictions (e.g. NYC Local Law 144, EU AI Act), so keep a human in the loop.



## Features

| Tab | What it does |
|---|---|
| 🌐 **Placement Matrix** | Evaluates each candidate against several company/role openings and shows selection chance per role plus the best-fit placement. |
| ⚡ **Bulk Screener** | Upload many PDFs, score them in parallel (10 worker threads), filter/search results, view charts, and export CSV or a shortlist summary. |
| 🎯 **ATS Diagnostic** | Single-resume audit: score, verdict, strengths, red flags, missing keywords and X-Y-Z bullet rewrites. |
| 📝 **Cover Letter** | Generates a tailored cover letter from a resume and job description. |
| ✨ **Bullet Polisher** | Rewrites bullets, LinkedIn summaries and project descriptions in three styles. |
| 💬 **Career Coach** | Chat-based mock interviews and career advice. |

**Other building blocks**
- **Resume pre-validator** – rejects non-resumes (bills, recipes, job postings, letters…) before spending an LLM call.
- **PII redaction (blind mode)** – masks name, email, phone, profile links, institution names and gendered pronouns before text is sent to the model.
- **Model failover** – tries a list of Gemini models in order if one fails.
- **Robust JSON parsing** – handles fenced output, extra text, string scores (`"78/100"`), truncated output; API failures are reported as errors, never as "Not a Resume".
- **Keyword fallback** – approximate role-fit scoring if the LLM returns unusable output.
- **Interview invitations** – simulated by default; real SMTP only if credentials are provided.

## Architecture

```
PDF upload
   │
   ▼
extract_text_from_pdf (pypdf)
   │
   ▼
validate_resume  ── rejects obvious non-resumes (no LLM cost)
   │
   ▼  (optional) mask_candidate_pii  ── blind-screening mode
   │
   ▼
Gemini (structured JSON prompt, model failover)
   │
   ▼
parse_evaluation ── ok / partial / error
   │
   ▼
Streamlit UI  (scores, charts, filters, CSV / summary export)
```

## Project structure

```
.
├── app.py                      # Streamlit entry point: login + tab layout
├── tabs/
│   ├── tab_multi_role_matcher.py
│   ├── tab_batch_screener.py
│   ├── tab_resume_score.py
│   ├── tab_cover_letter.py
│   ├── tab_quick_feedback.py
│   └── tab_career_coach.py
├── utils/
│   ├── auth.py                 # simple JSON-file user store
│   ├── resume_parser.py        # PDF text extraction, validator, PII masking
│   ├── llm_parse.py            # robust parsing of LLM output
│   ├── grok_client.py          # Gemini client (legacy file name) + failover
│   └── email_service.py        # interview invitation emails
├── requirements.txt
├── .env.example
└── README.md
```

## Getting started

**Requirements:** Python 3.10+ and a [Gemini API key](https://aistudio.google.com/).

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env        # then put your key in .env
python -m streamlit run app.py
```

`.env`:
```
GEMINI_API_KEY=your_key_here
```

Open http://localhost:8501 and create an account from the sign-up tab.

## Testing

The deterministic parts of the pipeline (everything that does not call Gemini) were tested on **synthetic data** across tech and non-tech roles, many resume layouts, and many non-resume document types.

| Component | Test set | Result |
|---|---|---|
| Resume validator | 450 synthetic cases (350 resumes, 100 non-resumes) | 100% of resumes accepted; 64% of non-resumes rejected by the validator alone¹ |
| Resume validator | 20 hand-written documents in new formats | 10/10 resumes accepted, 9/10 non-resumes rejected |
| PII redaction | 50 synthetic resumes (varied phone formats, links, institutions, names) | 50/50 on email, phone, name, links, institution; no over-redaction of content or metrics |
| LLM-output parsing | 50 malformed/odd outputs (trailing commas, single quotes, `"78/100"`, null scores, fenced blocks, truncation, API errors) | 50/50 |

¹ Document types that share resume vocabulary (SOPs, recommendation letters, resume-tips articles, READMEs) can pass the validator. They are caught by the LLM's own `is_valid_resume` check.

**Honest limitations**
- Test data is synthetic. Real-world accuracy has not been measured.
- LLM scoring quality itself has **not** been benchmarked against human recruiters.
- Only the validator, redaction and parsing layers are covered by tests. Live Gemini calls are non-deterministic and are checked manually.
- Name redaction relies on the name appearing on the first line of the resume.


## Tech stack

Python · Streamlit · Google Gemini (`google-generativeai`) · pypdf · pandas · Plotly

## License

MIT — see `LICENSE` (add one before publishing).
