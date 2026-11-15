# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
from utils.grok_client import configure_gemini, ACTIVE_MODELS

def render():
    st.markdown("## 💬 Executive Career Coach & Mock Interviewer")
    st.markdown('<p style="color:#64748B; margin-top:-10px;">Simulate technical/behavioral interviews, salary negotiations, or career transition strategies.</p>', unsafe_allow_html=True)

    if "coach_messages" not in st.session_state:
        st.session_state.coach_messages = [
            {
                "role": "model", 
                "content": "Hello! I am your Executive AI Career Coach. How can I help you today? You can ask me to conduct a mock interview for any role, evaluate your career pitch, or strategize an offer negotiation."
            }
        ]

    # Display chat history
    for msg in st.session_state.coach_messages:
        role_label = "assistant" if msg["role"] == "model" else "user"
        with st.chat_message(role_label):
            st.markdown(msg["content"])

    # User input
    user_input = st.chat_input("Ask a career question or say 'Start a mock interview for SDE role'...")
    if user_input:
        st.session_state.coach_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        if not configure_gemini():
            with st.chat_message("assistant"):
                st.error("⚠️ GEMINI_API_KEY is not configured in .env.")
            return

        with st.chat_message("assistant"):
            with st.spinner("Career Coach is formulating advice..."):
                history = []
                for m in st.session_state.coach_messages[:-1]:
                    history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
                
                success = False
                last_error = ""
                for m_name in ACTIVE_MODELS:
                    try:
                        model = genai.GenerativeModel(
                            model_name=m_name,
                            system_instruction="You are an empathetic, insightful, and strategic Executive Career Coach with 15+ years of talent acquisition experience. Provide practical, high-value, and actionable guidance in English."
                        )
                        chat = model.start_chat(history=history)
                        response = chat.send_message(user_input)
                        reply = response.text
                        st.markdown(reply)
                        st.session_state.coach_messages.append({"role": "model", "content": reply})
                        success = True
                        break
                    except Exception as e:
                        last_error = str(e)
                        continue

                if not success:
                    st.error(f"Error communicating with AI: {last_error}")
