"""User authentication and profile management."""
import hashlib
import json
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Dict

from config import USERS_DB_FILE, DEFAULT_QUERY_QUOTA

DB_FILE = Path(USERS_DB_FILE)
RESET_TOKENS = {}

def _load_users() -> Dict:
    """Load users from JSON database."""
    if not DB_FILE.exists():
        return {}
    return json.loads(DB_FILE.read_text())

def _save_users(users: Dict) -> None:
    """Save users to JSON database."""
    DB_FILE.write_text(json.dumps(users, indent=2))

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

# ========== AUTHENTICATION ==========

def signup(username: str, email: str, password: str) -> Tuple[bool, str]:
    """Create new user account."""
    users = _load_users()
    
    if username in users:
        return False, "Username already exists"
    if any(u.get("email") == email for u in users.values()):
        return False, "Email already registered"
    
    users[username] = {
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "query_quota": DEFAULT_QUERY_QUOTA
    }
    _save_users(users)
    return True, "Account created successfully"

def login(username: str, password: str) -> Tuple[bool, str]:
    """Authenticate user."""
    users = _load_users()
    
    if username not in users:
        return False, "Invalid credentials"
    if users[username]["password"] != hash_password(password):
        return False, "Invalid credentials"
    
    return True, "Login successful"

# ========== PROFILE MANAGEMENT ==========

def get_user_profile(username: str) -> Dict:
    """Get user profile information."""
    users = _load_users()
    if username not in users:
        return {}
    
    user = users[username]
    return {
        "username": username,
        "email": user.get("email", ""),
        "created_at": user.get("created_at", ""),
        "query_quota": user.get("query_quota", 0)
    }

def update_profile(username: str, new_username: str = None, new_email: str = None) -> Tuple[bool, str]:
    """Update user profile."""
    users = _load_users()
    
    if username not in users:
        return False, "User not found"
    
    # Update username
    if new_username and new_username != username:
        if new_username in users:
            return False, "Username taken"
        users[new_username] = users.pop(username)
        username = new_username
    
    # Update email
    if new_email:
        if any(u.get("email") == new_email for k, u in users.items() if k != username):
            return False, "Email already in use"
        users[username]["email"] = new_email
    
    _save_users(users)
    
    # Send notification
    try:
        from email_service import send_profile_updated_email
        send_profile_updated_email(users[username].get("email", ""), username)
    except:
        pass
    
    return True, username

# ========== PASSWORD MANAGEMENT ==========

def change_password(username: str, old_pass: str, new_pass: str) -> Tuple[bool, str]:
    """Change user password."""
    users = _load_users()
    
    if username not in users:
        return False, "User not found"
    if users[username]["password"] != hash_password(old_pass):
        return False, "Incorrect password"
    
    users[username]["password"] = hash_password(new_pass)
    _save_users(users)
    
    # Send notification
    try:
        from email_service import send_password_changed_email
        send_password_changed_email(users[username].get("email", ""), username)
    except:
        pass
    
    return True, "Password changed"

def request_reset(email: str) -> Tuple[bool, str, str]:
    """Request password reset token."""
    users = _load_users()
    username = next((k for k, v in users.items() if v.get("email") == email), None)
    
    if not username:
        return False, "Email not found", ""
    
    token = secrets.token_urlsafe(32)
    RESET_TOKENS[token] = {
        "username": username,
        "expires": datetime.now() + timedelta(hours=1)
    }
    
    return True, username, token

def reset_password(token: str, new_pass: str) -> Tuple[bool, str]:
    """Reset password using token."""
    if token not in RESET_TOKENS:
        return False, "Invalid token"
    
    if datetime.now() > RESET_TOKENS[token]["expires"]:
        del RESET_TOKENS[token]
        return False, "Token expired"
    
    username = RESET_TOKENS[token]["username"]
    users = _load_users()
    users[username]["password"] = hash_password(new_pass)
    _save_users(users)
    del RESET_TOKENS[token]
    
    # Send confirmation
    try:
        from email_service import send_password_changed_email
        send_password_changed_email(users[username].get("email", ""), username)
    except:
        pass
    
    return True, "Password reset successful"

# ========== QUOTA MANAGEMENT ==========

def get_user_quotas(username: str) -> Dict:
    """Get user quotas."""
    users = _load_users()
    if username not in users:
        return {"query_quota": 0}
    return {"query_quota": users[username].get("query_quota", 0)}

def decrement_quota(username: str, quota_type: str) -> bool:
    """Decrement user quota."""
    users = _load_users()
    if username not in users or users[username].get(quota_type, 0) <= 0:
        return False
    
    users[username][quota_type] -= 1
    _save_users(users)
    return True
