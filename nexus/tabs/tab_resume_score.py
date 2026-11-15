# -*- coding: utf-8 -*-
import streamlit as st
from utils.grok_client import evaluate_resume_structured
from utils.resume_parser import extract_text_from_pdf, validate_resume

def render():
    st.header("🎯 Deep ATS Resume Auditor & Optimizer")
    st.caption("AI-powered diagnostic scorecard covering ATS match, strengths, red flags, and Google X-Y-Z bullet enhancements.")

    uploaded_pdf = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"], key="score_pdf")
    resume_text = ""
    if uploaded_pdf:
        resume_text = extract_text_from_pdf(uploaded_pdf)
        if resume_text:
            st.success(f"Extracted readable text from **{uploaded_pdf.name}**")
        else:
            st.error("⚠️ Could not extract text from this PDF (it may be a scanned image without selectable text).")
    else:
        resume_text = st.text_area("Or Paste Resume Text", height=140, placeholder="Paste resume plain text here...")

    target_jd = st.text_area(
        "Target Job Description (Evaluates keyword coverage & alignment)", 
        height=120, 
        placeholder="Paste target job requirements (e.g. SDE-1, Data Analyst, Cloud Engineer)..."
    )

    if st.button("Audit & Score Resume 📊", type="primary", use_container_width=True):
        if not resume_text or len(resume_text.strip()) < 50:
            st.error("❌ Please provide a valid document with readable text.")
            return

        # Pre-validation check: Is it actually a resume?
        is_valid_doc, val_reason = validate_resume(resume_text)
        if not is_valid_doc:
            st.error(f"❌ Document Rejected: {val_reason}")
            st.warning("⚠️ This does not appear to be a candidate Resume or CV. Score: **0 / 100**.")
            return

        with st.spinner("Conducting comprehensive ATS and Recruiter audit..."):
            data = evaluate_resume_structured(resume_text, target_jd)

            if not data.get("is_valid_resume", True):
                st.error("❌ Evaluation Failed: The AI determined this document is NOT a valid resume.")
                st.metric("ATS Score", "0 / 100")
                st.info(data.get("summary", "Document rejected."))
                return

            score = data.get("ats_score", 0)
            verdict = data.get("verdict", "Evaluated")
            candidate = data.get("candidate_name", "Candidate")

            st.markdown("---")
            # Top Score Visual Cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall ATS Score", f"{score} / 100")
            with col2:
                st.metric("Recruiter Verdict", verdict)
            with col3:
                st.metric("Keyword Match", data.get("match_percentage", f"{score}%"))

            # Progress Bar with dynamic color indicator
            st.progress(min(max(score, 0), 100) / 100.0)

            st.markdown(f"### 📋 Executive Summary for **{candidate}**")
            st.info(data.get("summary", "Resume evaluated against industry requirements."))

            # Two Column Breakdown
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("#### ✅ Key Strengths")
                for s in data.get("strengths", []):
                    st.write(f"• {s}")

                st.markdown("#### 🔑 Missing Keywords")
                missing = data.get("missing_keywords", [])
                if missing:
                    st.write("Add these terms to bypass ATS filters:")
                    st.write(", ".join([f"`{k}`" for k in missing]))
                else:
                    st.write("All core industry keywords identified!")

            with c_right:
                st.markdown("#### ⚠️ Red Flags & Weak Areas")
                for r in data.get("red_flags", []):
                    st.write(f"• {r}")

            # Before & After Improvements
            improvements = data.get("key_improvements", [])
            if improvements:
                st.markdown("---")
                st.markdown("### 🔄 High-Impact Bullet Rewrites (Google X-Y-Z Method)")
                for imp in improvements:
                    with st.container():
                        st.markdown(f"**Original:** `{imp.get('before', '')}`")
                        st.markdown(f"**Optimized Rewrite:** :green[**{imp.get('after', '')}**]")
                        st.markdown("")
