# -*- coding: utf-8 -*-
import streamlit as st
from utils.grok_client import query_gemini
from utils.resume_parser import extract_text_from_pdf, validate_resume

def render():
    st.markdown("## 📝 Tailored Cover Letter Generator")
    st.markdown('<p style="color:#64748B; margin-top:-10px;">Generate customized, executive-tier cover letters aligned to exact job requirements.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Candidate Background")
        pdf_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="cl_pdf")
        user_resume = ""
        if pdf_file:
            user_resume = extract_text_from_pdf(pdf_file)
            is_valid, _ = validate_resume(user_resume)
            if is_valid:
                st.success(f"Verified resume content from **{pdf_file.name}**")
            else:
                st.warning("⚠️ Uploaded PDF may not be a standard resume, but you can still proceed.")
        else:
            user_resume = st.text_area("Or Paste Candidate Resume / Experience", height=180, placeholder="Paste resume plain text here...")

    with col2:
        st.subheader("2. Target Role & Company")
        job_role = st.text_input("Target Job Title", placeholder="e.g. Senior Software Engineer / SDE-1")
        company = st.text_input("Target Company", placeholder="e.g. Google, Microsoft, Amazon")
        job_desc = st.text_area("Job Description / Key Qualifications", height=130, placeholder="Paste the key responsibilities and requirements...")

    tone = st.selectbox(
        "Tone of Voice", 
        ["Executive & Authoritative", "Engineering Excellence (Data & Metrics Driven)", "Dynamic & Confident", "Direct & Concise"]
    )

    if st.button("Generate Professional Cover Letter 🚀", type="primary", use_container_width=True):
        if not user_resume or not job_desc:
            st.error("Please provide both your Resume/background and the Job Description.")
            return

        with st.spinner("AI is synthesizing candidate experience with target job competencies..."):
            prompt = f"""Write an outstanding, customized cover letter for:
Job Role: {job_role}
Company: {company}
Tone: {tone}

Target Job Description:
{job_desc}

Candidate Resume / Details:
{user_resume}

Guidelines:
- Match candidate achievements directly to specific job requirements.
- Use strong action verbs, quantifiable metrics, and clear impact.
- Avoid generic cliches (e.g., 'I am writing to express my interest').
- Make it ready-to-send with a professional layout and placeholder brackets for dates/addresses.
"""
            result = query_gemini(prompt)
            st.markdown("---")
            st.markdown("### 📄 Generated Cover Letter")
            st.markdown(result)
            st.download_button(
                label="📥 Download Cover Letter (.txt)",
                data=result,
                file_name=f"cover_letter_{company.replace(' ', '_').lower()}.txt",
                mime="text/plain",
                use_container_width=True
            )
