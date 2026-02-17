"""Email notification service with HTML templates."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, FRONTEND_URL

def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send HTML email."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("⚠️  Email not configured")
        return False
    
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
        print(f"❌ Email error: {e}")
        return False

def _email_template(title: str, content: str, color: str = "#00ff88") -> str:
    """Base email template."""
    return f"""
    <html><body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:40px 0">
    <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)">
    <tr><td style="background:linear-gradient(135deg,{color},{color});padding:30px;text-align:center;border-radius:8px 8px 0 0">
    <h1 style="color:#fff;margin:0;font-size:28px">{title}</h1>
    </td></tr>
    <tr><td style="padding:40px 30px">{content}</td></tr>
    <tr><td style="background:#f9f9f9;padding:20px 30px;text-align:center;border-radius:0 0 8px 8px">
    <p style="color:#999;font-size:12px;margin:0">© 2026 RAG PDF Chat</p>
    </td></tr>
    </table>
    </td></tr>
    </table>
    </body></html>
    """

def send_welcome_email(email: str, username: str) -> bool:
    """Send welcome email on signup."""
    content = f"""
    <h2 style="color:#333;margin:0 0 20px">Hi {username}!</h2>
    <p style="color:#666;line-height:1.6;margin:0 0 15px">Your account has been successfully created.</p>
    <p style="color:#666;line-height:1.6;margin:0 0 15px">You can now:</p>
    <ul style="color:#666;line-height:1.8">
    <li>Upload PDF documents</li>
    <li>Chat with your documents using AI</li>
    <li>Manage your profile and settings</li>
    </ul>
    <div style="text-align:center;margin:30px 0">
    <a href="{FRONTEND_URL}" style="background:#00ff88;color:#000;padding:12px 30px;text-decoration:none;border-radius:5px;font-weight:bold;display:inline-block">Get Started</a>
    </div>
    <p style="color:#999;font-size:12px;margin:20px 0 0">If this wasn't you, please contact support immediately.</p>
    """
    return send_email(email, "Welcome to RAG PDF Chat 🚀", _email_template("🚀 Welcome to RAG PDF Chat", content))

def send_reset_email(email: str, username: str, token: str) -> bool:
    """Send password reset email."""
    reset_link = f"{FRONTEND_URL}/reset-password.html?token={token}"
    content = f"""
    <h2 style="color:#333;margin:0 0 20px">Hi {username},</h2>
    <p style="color:#666;line-height:1.6;margin:0 0 15px">We received a request to reset your password.</p>
    <p style="color:#666;line-height:1.6;margin:0 0 25px">Click the button below to reset your password:</p>
    <div style="text-align:center;margin:30px 0">
    <a href="{reset_link}" style="background:#ff6b6b;color:#fff;padding:12px 30px;text-decoration:none;border-radius:5px;font-weight:bold;display:inline-block">Reset Password</a>
    </div>
    <p style="color:#999;font-size:13px;margin:25px 0 0">This link expires in 1 hour.</p>
    <div style="background:#fff3cd;padding:15px;border-left:4px solid #ffc107;margin-top:20px">
    <p style="color:#856404;font-size:13px;margin:0"><strong>⚠️ Security Notice:</strong> If you didn't request this, please ignore this email.</p>
    </div>
    """
    return send_email(email, "Password Reset Request 🔒", _email_template("🔒 Password Reset", content, "#ff6b6b"))

def send_password_changed_email(email: str, username: str) -> bool:
    """Send password changed confirmation."""
    content = f"""
    <h2 style="color:#333;margin:0 0 20px">Hi {username},</h2>
    <p style="color:#666;line-height:1.6;margin:0 0 15px">Your password has been successfully changed.</p>
    <p style="color:#666;line-height:1.6;margin:0 0 15px">You can now log in with your new password.</p>
    <div style="background:#fff3cd;padding:15px;border-left:4px solid #ffc107;margin-top:20px">
    <p style="color:#856404;font-size:13px;margin:0"><strong>⚠️ Security Notice:</strong> If you didn't make this change, contact support immediately.</p>
    </div>
    """
    return send_email(email, "Password Changed Successfully ✅", _email_template("✅ Password Changed", content))

def send_profile_updated_email(email: str, username: str) -> bool:
    """Send profile updated confirmation."""
    content = f"""
    <h2 style="color:#333;margin:0 0 20px">Hi {username},</h2>
    <p style="color:#666;line-height:1.6;margin:0 0 15px">Your profile information has been successfully updated.</p>
    <div style="background:#fff3cd;padding:15px;border-left:4px solid #ffc107;margin-top:20px">
    <p style="color:#856404;font-size:13px;margin:0"><strong>⚠️ Security Notice:</strong> If you didn't make this change, contact support immediately.</p>
    </div>
    """
    return send_email(email, "Profile Updated Successfully ✅", _email_template("✅ Profile Updated", content))
