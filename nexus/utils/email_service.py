# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_interview_invitation(smtp_user: str, smtp_pass: str, recipient_email: str, candidate_name: str, company_name: str, role_title: str) -> tuple[bool, str]:
    """Sends an automated interview invitation email via SMTP."""
    if not recipient_email or "@" not in recipient_email:
        return False, "Invalid candidate email address."

    subject = f"Interview Invitation: {role_title} at {company_name}"
    
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #E2E8F0; border-radius: 8px;">
          <h2 style="color: #0284C7;">Congratulations, {candidate_name}!</h2>
          <p>We were highly impressed by your qualifications and project background during our automated ATS evaluation for the <b>{role_title}</b> position at <b>{company_name}</b>.</p>
          <div style="background: #F0FDF4; border-left: 4px solid #16A34A; padding: 12px; margin: 16px 0; border-radius: 4px;">
            <p style="margin: 0; color: #15803D; font-weight: 600;">Status: Shortlisted for Technical Assessment & Hiring Round</p>
          </div>
          <p>Our talent acquisition team would like to invite you for a 45-minute technical discussion round.</p>
          <p>Please reply directly to this email with your availability over the upcoming week.</p>
          <br>
          <p style="color: #64748B; font-size: 0.9rem;">Best regards,<br><b>Talent Acquisition Team</b><br>{company_name}</p>
        </div>
      </body>
    </html>
    """

    # If mock credentials or empty, simulate high-fidelity dispatch
    if not smtp_user or not smtp_pass or smtp_user == "mock":
        return True, f"Simulated Dispatch: Email successfully dispatched to {recipient_email}"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_body, "html"))

        # Gmail / Standard SMTP port 587
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient_email, msg.as_string())
        return True, f"Official email dispatched to {recipient_email}"
    except Exception as e:
        return False, f"SMTP Connection Notice: {str(e)}"
