"""Email notification service."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import *

def _send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email via SMTP."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print(f"\n[Email] To: {to_email} | Subject: {subject}\n{body}\n")
        return True
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_welcome_email(email: str, username: str) -> bool:
    subject = "Welcome to RAG PDF Chat!"
    body = f"""
    <h2>Welcome {username}!</h2>
    <p>Your account has been created successfully.</p>
    <p>You can now upload PDFs and ask questions about them.</p>
    """
    return _send_email(email, subject, body)

def send_reset_email(email: str, username: str, token: str) -> bool:
    reset_link = f"http://localhost:3000/reset-password.html?token={token}"
    subject = "Password Reset Request"
    body = f"""
    <h2>Password Reset</h2>
    <p>Hi {username},</p>
    <p>Click the link below to reset your password:</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    <p>This link expires in 1 hour.</p>
    """
    return _send_email(email, subject, body)

def send_password_changed_email(email: str, username: str) -> bool:
    subject = "Password Changed"
    body = f"""
    <h2>Password Changed</h2>
    <p>Hi {username},</p>
    <p>Your password has been changed successfully.</p>
    """
    return _send_email(email, subject, body)

def send_profile_updated_email(email: str, username: str) -> bool:
    subject = "Profile Updated"
    body = f"""
    <h2>Profile Updated</h2>
    <p>Hi {username},</p>
    <p>Your profile has been updated successfully.</p>
    """
    return _send_email(email, subject, body)
