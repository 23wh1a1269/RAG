"""JWT-based authentication system."""
import hashlib
import json
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
import jwt
from fastapi import HTTPException, Header

from backend.config import *

DB_FILE = Path(USERS_DB_FILE)
RESET_TOKENS = {}

def _load_users() -> Dict:
    if not DB_FILE.exists():
        return {}
    return json.loads(DB_FILE.read_text())

def _save_users(users: Dict) -> None:
    DB_FILE.write_text(json.dumps(users, indent=2))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username: str) -> str:
    """Generate JWT token."""
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """Verify JWT and return username."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ========== AUTHENTICATION ==========

def signup(username: str, email: str, password: str) -> Tuple[bool, str]:
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

def login(username: str, password: str) -> Tuple[bool, str, str]:
    """Returns (success, message, token)."""
    users = _load_users()
    
    if username not in users or users[username]["password"] != hash_password(password):
        return False, "Invalid credentials", ""
    
    token = create_token(username)
    return True, "Login successful", token

# ========== PROFILE ==========

def get_user_profile(username: str) -> Dict:
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
    users = _load_users()
    
    if username not in users:
        return False, "User not found"
    
    if new_username and new_username != username:
        if new_username in users:
            return False, "Username taken"
        users[new_username] = users.pop(username)
        username = new_username
    
    if new_email:
        if any(u.get("email") == new_email for k, u in users.items() if k != username):
            return False, "Email already in use"
        users[username]["email"] = new_email
    
    _save_users(users)
    
    try:
        from backend.email_service import send_profile_updated_email
        send_profile_updated_email(users[username].get("email", ""), username)
    except:
        pass
    
    return True, username

# ========== PASSWORD ==========

def change_password(username: str, old_pass: str, new_pass: str) -> Tuple[bool, str]:
    users = _load_users()
    
    if username not in users or users[username]["password"] != hash_password(old_pass):
        return False, "Incorrect password"
    
    users[username]["password"] = hash_password(new_pass)
    _save_users(users)
    
    try:
        from backend.email_service import send_password_changed_email
        send_password_changed_email(users[username].get("email", ""), username)
    except:
        pass
    
    return True, "Password changed"

def request_reset(email: str) -> Tuple[bool, str]:
    users = _load_users()
    username = next((k for k, v in users.items() if v.get("email") == email), None)
    
    if not username:
        return True, "If the email is registered, a reset link has been sent."
    
    token = secrets.token_urlsafe(32)
    RESET_TOKENS[token] = {
        "username": username,
        "expires": datetime.now() + timedelta(hours=1)
    }
    
    try:
        from backend.email_service import send_reset_email
        send_reset_email(email, username, token)
    except Exception as e:
        print(f"Email error: {e}")
    
    return True, "If the email is registered, a reset link has been sent."

def reset_password(token: str, new_pass: str) -> Tuple[bool, str]:
    if token not in RESET_TOKENS:
        return False, "Invalid or expired token"
    
    if datetime.now() > RESET_TOKENS[token]["expires"]:
        del RESET_TOKENS[token]
        return False, "Token expired"
    
    username = RESET_TOKENS[token]["username"]
    users = _load_users()
    users[username]["password"] = hash_password(new_pass)
    _save_users(users)
    del RESET_TOKENS[token]
    
    try:
        from backend.email_service import send_password_changed_email
        send_password_changed_email(users[username].get("email", ""), username)
    except:
        pass
    
    return True, "Password reset successful"

# ========== QUOTA ==========

def get_user_quotas(username: str) -> Dict:
    users = _load_users()
    if username not in users:
        return {"query_quota": 0}
    return {"query_quota": users[username].get("query_quota", 0)}

def decrement_quota(username: str, quota_type: str) -> bool:
    users = _load_users()
    if username not in users or users[username].get(quota_type, 0) <= 0:
        return False
    
    users[username][quota_type] -= 1
    _save_users(users)
    return True
