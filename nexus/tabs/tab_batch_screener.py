# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor
from utils.resume_parser import extract_text_from_pdf, validate_resume, mask_candidate_pii
from utils.grok_client import evaluate_resume_structured
from utils.email_service import send_interview_invitation

def process_single_pdf(pdf, target_jd, enable_bias_free=False):
    """Processes a single PDF with optional bias-free masking and strict verification."""
    try:
        raw_text = extract_text_from_pdf(pdf)
        if not raw_text or len(raw_text.strip()) < 50:
            return {
                "Rank": 0,
                "Candidate Name": pdf.name,
                "Email": "N/A",
                "Score": 0,
                "Verdict": "Unreadable / Empty PDF",
                "Top Strengths": "N/A",
                "Missing Skills": "N/A",
                "Summary": "PDF contains no selectable text or is an unreadable scan."
            }

        is_valid, reason = validate_resume(raw_text)
        if not is_valid:
            return {
                "Rank": 0,
                "Candidate Name": pdf.name,
                "Email": "N/A",
                "Score": 0,
                "Verdict": "Rejected - Not a Resume",
                "Top Strengths": "None",
                "Missing Skills": "N/A",
                "Summary": f"Document invalid: {reason}"
            }

        eval_text = raw_text
        extracted_pii = {}
        if enable_bias_free:
            eval_text, extracted_pii = mask_candidate_pii(raw_text)

        data = evaluate_resume_structured(eval_text, target_jd)
        
        if not data.get("is_valid_resume", True):
            return {
                "Rank": 0,
                "Candidate Name": pdf.name,
                "Email": "N/A",
                "Score": 0,
                "Verdict": "Rejected - Not a Resume",
                "Top Strengths": "None",
                "Missing Skills": "N/A",
                "Summary": data.get("summary", "Document is not a recognized resume.")
            }

        cand_name = data.get("candidate_name")
        if enable_bias_free or not cand_name or cand_name.lower() in ["candidate", "unknown", "none", "applicant", "[individual]"]:
            cand_name = f"Candidate-{pdf.name.replace('.pdf', '')[:8].upper()}" if enable_bias_free else pdf.name.replace(".pdf", "").replace("_", " ").title()

        # Capture actual email from raw text for one-click invite
        email_cand = extracted_pii.get("email") if extracted_pii.get("email") else "contact@candidate.com"

        strengths = "; ".join(data.get("strengths", [])[:2])
        missing = ", ".join(data.get("missing_keywords", [])[:3])

        return {
            "Rank": 0,
            "Candidate Name": cand_name,
            "Email": email_cand,
            "Score": data.get("ats_score", 0),
            "Verdict": data.get("verdict", "Evaluated"),
            "Top Strengths": strengths if strengths else "Profile parsed",
            "Missing Skills": missing if missing else "None specified",
            "Summary": data.get("summary", "")
        }
    except Exception as e:
        return {
            "Rank": 0,
            "Candidate Name": pdf.name,
            "Email": "N/A",
            "Score": 0,
            "Verdict": "Error",
            "Top Strengths": "N/A",
            "Missing Skills": "N/A",
            "Summary": f"Processing error: {str(e)}"
        }

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #334155;">
        <h2 style="color: #FFFFFF; margin: 0; font-size: clamp(1.2rem, 3vw, 1.6rem); font-weight: 700;">⚡ Enterprise Candidate Screener</h2>
        <p style="color: #94A3B8; margin: 6px 0 0 0; font-size: clamp(0.85rem, 2vw, 0.95rem); line-height: 1.5;">
            Autonomous high-throughput screening engine with real-time talent analytics, bias-free blind hiring mode, and one-click interview invitation dispatch.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Bias-Free Hiring Toggle
    bias_free_toggle = st.toggle("🛡️ Enable Bias-Free / Blind Hiring Mode (Masks Name, Gender, College & Contact PII)", value=False)
    if bias_free_toggle:
        st.info("🛡️ **Blind Hiring Active:** AI and Hiring Managers will evaluate solely on technical merit, projects, and skills. Names, colleges, and contact info are masked.")

    target_jd = st.text_area(
        "🎯 Benchmark Job Description / Competency Matrix",
        height=110,
        placeholder="Paste role requirements, tech stack (e.g. SDE-2, Full Stack, ML Engineer, Staff Architect)..."
    )

    uploaded_files = st.file_uploader(
        "📂 Candidate Resumes Repository (Upload single or 1,000+ PDFs simultaneously)",
        type=["pdf"],
        accept_multiple_files=True,
        key="batch_pdf_uploader"
    )

    if uploaded_files:
        st.markdown(f"""
        <div style="background: #F0FDF4; border-left: 4px solid #16A34A; padding: 10px 14px; border-radius: 6px; margin: 10px 0;">
            <span style="color: #15803D; font-weight: 600; font-size: 0.9rem;">✓ Ready for Batch Pipeline:</span> 
            <span style="color: #166534; font-size: 0.88rem;">{len(uploaded_files)} candidate documents loaded.</span>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        start_eval = st.button("🚀 Execute Enterprise Batch Screening", type="primary", use_container_width=True)

    if start_eval and uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        total = len(uploaded_files)

        results = []
        status_text.markdown(f"**⚡ Multi-threading active:** Processing {total} candidates concurrently...")

        max_workers = min(10, total)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_single_pdf, pdf, target_jd, bias_free_toggle) for pdf in uploaded_files]
            
            for idx, future in enumerate(futures):
                res = future.result()
                results.append(res)
                progress_bar.progress((idx + 1) / total)
                status_text.text(f"Evaluated {idx + 1} of {total} candidates ({int((idx + 1)/total * 100)}%)...")

        status_text.success("🎉 Enterprise Pipeline Screening Completed Successfully!")

        df = pd.DataFrame(results)
        df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
        df["Rank"] = df.index + 1
        st.session_state.batch_results = df

    # Display results if available in session state
    if "batch_results" in st.session_state and not st.session_state.batch_results.empty:
        df = st.session_state.batch_results

        st.markdown("---")
        st.markdown("### 📊 Executive Talent Analytics & Market Insights")

        # Top Metric Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        total = len(df)
        valid_df = df[df["Score"] > 0]
        avg_score = int(valid_df["Score"].mean()) if len(valid_df) > 0 else 0
        top_score = int(df["Score"].max())
        shortlisted = len(df[df["Score"] >= 75])

        with col_m1:
            st.metric("Total Candidates", total)
        with col_m2:
            st.metric("Top Benchmark", f"{top_score} / 100")
        with col_m3:
            st.metric("Talent Pool Average", f"{avg_score} / 100")
        with col_m4:
            st.metric("Shortlisted (>=75%)", shortlisted)

        # ----------------- 1. INTERACTIVE CHARTS & VISUALS -----------------
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            def get_category(score):
                if score >= 75:
                    return "Strong Match (>=75%)"
                elif score >= 50:
                    return "Potential Match (50-74%)"
                elif score > 0:
                    return "Needs Development (<50%)"
                return "Rejected / Non-Resume (0%)"

            df["Category"] = df["Score"].apply(get_category)
            cat_counts = df["Category"].value_counts().reset_index()
            cat_counts.columns = ["Verdict", "Count"]

            fig_donut = px.pie(
                cat_counts, 
                values="Count", 
                names="Verdict",
                hole=0.45,
                color="Verdict",
                color_discrete_map={
                    "Strong Match (>=75%)": "#10B981",
                    "Potential Match (50-74%)": "#F59E0B",
                    "Needs Development (<50%)": "#EF4444",
                    "Rejected / Non-Resume (0%)": "#64748B"
                },
                title="<b>Candidate Match Distribution</b>"
            )
            fig_donut.update_layout(
                margin=dict(t=40, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                height=320
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with chart_col2:
            all_missing = []
            for skills in df[df["Score"] > 0]["Missing Skills"]:
                if skills and skills != "N/A" and skills != "None specified":
                    for s in skills.split(","):
                        cleaned_skill = s.strip().title()
                        if cleaned_skill and len(cleaned_skill) > 2:
                            all_missing.append(cleaned_skill)

            skill_counts = Counter(all_missing).most_common(6)
            if skill_counts:
                skill_df = pd.DataFrame(skill_counts, columns=["Skill", "Frequency"])
                fig_bar = px.bar(
                    skill_df,
                    x="Frequency",
                    y="Skill",
                    orientation="h",
                    color="Frequency",
                    color_continuous_scale="Blues",
                    title="<b>Top Missing Competencies in Pool</b>"
                )
                fig_bar.update_layout(
                    yaxis=dict(autorange="reversed"),
                    margin=dict(t=40, b=10, l=10, r=10),
                    coloraxis_showscale=False,
                    height=320
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No significant skill gaps identified across valid profiles.")

        # ----------------- 2. SEARCH & FILTER CONTROLS -----------------
        st.markdown("---")
        st.markdown("### 🔍 Candidate Search & Advanced Filtering")
        
        f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 1])
        with f_col1:
            search_query = st.text_input("🔎 Search by Candidate Name or Skills", placeholder="e.g. Python, AWS, Docker...")
        with f_col2:
            min_score = st.slider("🎯 Filter by Minimum Score", min_value=0, max_value=100, value=0, step=5)
        with f_col3:
            verdict_filter = st.selectbox("Status Filter", ["All Candidates", "Strong Match Only (>=75)", "Potential Only (50-74)", "Valid Resumes Only (>0)"])

        filtered_df = df.copy()
        if min_score > 0:
            filtered_df = filtered_df[filtered_df["Score"] >= min_score]

        if verdict_filter == "Strong Match Only (>=75)":
            filtered_df = filtered_df[filtered_df["Score"] >= 75]
        elif verdict_filter == "Potential Only (50-74)":
            filtered_df = filtered_df[(filtered_df["Score"] >= 50) & (filtered_df["Score"] < 75)]
        elif verdict_filter == "Valid Resumes Only (>0)":
            filtered_df = filtered_df[filtered_df["Score"] > 0]

        if search_query:
            q = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df["Candidate Name"].str.lower().str.contains(q, na=False) |
                filtered_df["Top Strengths"].str.lower().str.contains(q, na=False) |
                filtered_df["Missing Skills"].str.lower().str.contains(q, na=False)
            ]

        st.caption(f"Showing **{len(filtered_df)}** of **{total}** candidates matching criteria.")

        st.dataframe(
            filtered_df[["Rank", "Candidate Name", "Score", "Verdict", "Missing Skills", "Top Strengths"]],
            use_container_width=True,
            height=360
        )

        # ----------------- 3. AUTOMATED EMAIL DISPATCH SUITE -----------------
        st.markdown("---")
        st.markdown("### 📧 Automated Interview Invitation Dispatch Suite")
        st.caption("One-click automated email invitations dispatched to all top shortlisted candidates.")

        with st.expander("⚙️ Configure SMTP Email Credentials (Optional / Simulated by default)"):
            c_e1, c_e2, c_e3 = st.columns(3)
            with c_e1:
                smtp_user = st.text_input("Sender Email (e.g. hiring@company.com)", value="mock")
            with c_e2:
                smtp_pass = st.text_input("App Password", type="password")
            with c_e3:
                comp_name = st.text_input("Company Name for Email", value="TalentPulse Global")

        top_candidates = df[df["Score"] >= 70].head(10)
        
        col_em1, col_em2 = st.columns([2.5, 3.5])
        with col_em1:
            send_invites = st.button(f"✉️ Dispatch Interview Invites to Top {len(top_candidates)} Shortlisted Candidates", type="primary", use_container_width=True)

        if send_invites:
            if top_candidates.empty:
                st.warning("No candidates scored >= 70 for shortlisting.")
            else:
                sent_count = 0
                for _, cand in top_candidates.iterrows():
                    success, msg = send_interview_invitation(
                        smtp_user, 
                        smtp_pass, 
                        cand["Email"], 
                        cand["Candidate Name"], 
                        comp_name if comp_name else "TalentPulse", 
                        target_jd[:30] if target_jd else "Engineering Role"
                    )
                    if success:
                        sent_count += 1
                st.success(f"🎉 Successfully dispatched {sent_count} interview invitations to shortlisted candidates!")

        # ----------------- 4. EXPORT BUTTONS -----------------
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Full Filtered Candidates (.CSV)",
                data=csv_data,
                file_name="candidate_screening_report.csv",
                mime="text/csv",
                type="secondary",
                use_container_width=True
            )

        with exp_col2:
            top_10 = df[df["Score"] >= 70].head(10)
            if top_10.empty:
                top_10 = df.head(10)

            email_summary = "# 🚀 TOP SHORTLISTED CANDIDATES SUMMARY\n"
            email_summary += f"Role Context: {target_jd[:100] if target_jd else 'General Tech Engineering'}\n"
            email_summary += f"Total Pool Screened: {len(df)} | Shortlisted: {len(top_10)}\n"
            email_summary += "="*65 + "\n\n"

            for _, row in top_10.iterrows():
                email_summary += f"★ Rank #{row['Rank']} - {row['Candidate Name']} | ATS Score: {row['Score']}/100 ({row['Verdict']})\n"
                email_summary += f"  • Top Strengths: {row['Top Strengths']}\n"
                email_summary += f"  • Missing Competencies: {row['Missing Skills']}\n"
                email_summary += f"  • Recruiter Summary: {row['Summary']}\n\n"

            email_summary += "="*65 + "\nGenerated via TalentPulse AI Enterprise Platform."

            st.download_button(
                label="⚡ Download Top Shortlisted Summary (Email Ready .TXT)",
                data=email_summary,
                file_name="top_shortlisted_candidates_summary.txt",
                mime="text/plain",
                type="primary",
                use_container_width=True
            )
