# -*- coding: utf-8 -*-
import streamlit as st
from utils.grok_client import query_gemini

def render():
    st.header("⚡ Quick Bullet Point & Bio Polisher")
    st.caption("Instantly rewrite individual bullets, LinkedIn summaries, or project descriptions to top-tier industry standards.")

    option = st.radio(
        "Select what you want to optimize:", 
        [
            "Transform Bullet Point into High-Impact Achievement",
            "LinkedIn Headline & Summary",
            "Project Description for Tech Resume"
        ], 
        horizontal=True
    )

    input_text = st.text_area(
        "Enter your rough draft or existing bullet point:", 
        height=140, 
        placeholder="e.g. Worked on payment gateway and fixed bugs in checkout system."
    )

    if st.button("Polish & Elevate ✨", type="primary", use_container_width=True):
        if not input_text.strip():
            st.warning("Please enter some text to polish.")
            return

        with st.spinner("Polishing with AI..."):
            prompt = f"""
Task: Optimize the following career text for maximum recruiter impact:
Type: {option}
Input Text:
{input_text}

Instructions:
- Provide 3 distinct variations:
  1. High-Metric & Impact Oriented (for FAANG / top-tier firms)
  2. Concise & Direct (for strict ATS scanners)
  3. Leadership & Ownership Driven
- Highlight what was improved and why it delivers better results.
"""
            result = query_gemini(prompt)
            st.markdown(result)
