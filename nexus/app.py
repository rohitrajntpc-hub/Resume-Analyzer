# -*- coding: utf-8 -*-
import os
import streamlit as st
from dotenv import load_dotenv
from utils.auth import authenticate_user, signup_user

# High-Caliber Page Config
st.set_page_config(
    page_title="NexusATS | Autonomous AI Talent Intelligence Matrix",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, Native Dark/Light Adaptive CSS (Fixes Cutoff & Overflow)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Viewport Padding - Gives natural breathing room */
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1400px;
    }
    
    /* TABS FIX: Clean native tabs without custom border overlap */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        padding-bottom: 8px !important;
        margin-bottom: 24px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto !important;
        padding: 10px 18px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        background-color: transparent !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #0284C7 !important;
        color: #FFFFFF !important;
        border: 1px solid #0284C7 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }
    
    /* Executive Metric Display */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #38BDF8 !important;
        letter-spacing: -0.5px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Action Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.4rem;
        min-height: 44px;
        background: #0284C7 !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4);
    }
    
    /* Recruiter Executive ID Card in Sidebar */
    .nexus-badge {
        background: #1E293B;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #334155;
        color: white;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# ----------------- RECRUITER AUTHENTICATION GATEWAY -----------------
if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; margin-bottom: 25px;">
        <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(2, 132, 199, 0.1); border: 1px solid rgba(2, 132, 199, 0.3); padding: 6px 16px; border-radius: 30px; margin-bottom: 14px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #38BDF8; border-radius: 50%;"></span>
            <span style="color: #38BDF8; font-weight: 700; font-size: 0.82rem; letter-spacing: 0.5px;">NEXUS TALENT INTELLIGENCE OS</span>
        </div>
        <h1 style="font-weight: 800; font-size: 2.6rem; margin: 0; letter-spacing: -1px;">
            NexusATS <span style="color: #38BDF8;">Engine</span>
        </h1>
        <p style="color: #94A3B8; font-size: 1.05rem; max-width: 620px; margin: 10px auto 0 auto; line-height: 1.5;">
            Autonomous neural talent acquisition platform. Multi-role vector mapping, bias-free screening, and automated candidate shortlisting.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔐 Recruiter Sign In", "📝 Create Enterprise Account"])

        with auth_tab1:
            st.markdown("#### Enterprise Access Portal")
            login_email = st.text_input("Corporate Work Email", placeholder="recruiter@enterprise.com", key="login_email")
            login_pw = st.text_input("Security Key / Password", type="password", key="login_pw")
            
            if st.button("Authenticate & Access Matrix 🚀", type="primary", use_container_width=True):
                success, user = authenticate_user(login_email, login_pw)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user
                    st.rerun()
                else:
                    st.error("Authentication failed. Please check credentials or create an enterprise account.")

            st.caption("Demo Recruiter Access: `admin@careerai.com` | Password: `admin123`")

        with auth_tab2:
            st.markdown("#### Register New Account")
            reg_name = st.text_input("Full Name", placeholder="e.g. Sarah Jenkins", key="reg_name")
            reg_email = st.text_input("Corporate Email", placeholder="e.g. s.jenkins@enterprise.com", key="reg_email")
            reg_pw = st.text_input("Create Password", type="password", key="reg_pw")
            reg_role = st.selectbox(
                "Corporate Designation", 
                ["Global Head of Talent Acquisition", "Senior Technical Recruiter", "Staff Engineering Hiring Manager", "AI Workforce Architect", "Candidate / Job Seeker"], 
                key="reg_role"
            )

            if st.button("Initialize Account & Access Platform ✨", type="primary", use_container_width=True):
                success, msg = signup_user(reg_name, reg_email, reg_pw, reg_role)
                if success:
                    st.success(msg)
                    _, user = authenticate_user(reg_email, reg_pw)
                    st.session_state.authenticated = True
                    st.session_state.user_info = user
                    st.rerun()
                else:
                    st.error(msg)
    st.stop()

# ----------------- MAIN LOGGED-IN STUDIO DASHBOARD -----------------

with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;">
        <span style="font-size: 1.5rem; color: #38BDF8;">💠</span>
        <span style="font-weight: 800; font-size: 1.3rem; letter-spacing: -0.6px;">NexusATS</span>
    </div>
    <p style="color: #94A3B8; font-size: 0.78rem; margin-top: -4px; margin-bottom: 12px;">Autonomous Talent Operating System</p>
    """, unsafe_allow_html=True)
    
    # Executive Recruiter Badge
    st.markdown(f"""
    <div class="nexus-badge">
        <div style="font-size: 0.7rem; color: #38BDF8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Active Operator</div>
        <div style="font-weight: 700; font-size: 0.94rem; margin-top: 2px;">{st.session_state.user_info.get('name', 'Talent Lead')}</div>
        <div style="font-size: 0.76rem; color: #94A3B8; margin-top: 1px;">{st.session_state.user_info.get('role', 'Recruiter')}</div>
        <div style="font-size: 0.72rem; color: #38BDF8; margin-top: 3px; font-family: monospace;">{st.session_state.user_info.get('email', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_info = {}
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚡ Infrastructure Metrics")
    st.markdown("• **Neural Engine:** Gemini Flash 3.1 Core")
    st.markdown("• **Throughput:** 10,000+ Profiles / Batch")
    st.markdown("• **Vector Alignment:** Multi-Role Matrix Active")
    st.markdown("• **Fairness Engine:** Bias-Free Blind Hiring Active")

    st.markdown("---")
    st.caption("NexusATS v5.0 | Studio Enterprise")

# Import Modules
from tabs import (
    tab_multi_role_matcher,
    tab_batch_screener,
    tab_resume_score,
    tab_cover_letter,
    tab_quick_feedback,
    tab_career_coach
)

# Clean, Native Tab Bar (Zero Overlap & Zero Cutoff)
tabs = st.tabs([
    "🌐 Placement Matrix",
    "⚡ Bulk Screener",
    "🎯 ATS Diagnostic",
    "📝 Cover Letter",
    "✨ Bullet Polisher",
    "💬 Career Coach"
])

with tabs[0]:
    tab_multi_role_matcher.render()

with tabs[1]:
    tab_batch_screener.render()

with tabs[2]:
    tab_resume_score.render()

with tabs[3]:
    tab_cover_letter.render()

with tabs[4]:
    tab_quick_feedback.render()

with tabs[5]:
    tab_career_coach.render()
