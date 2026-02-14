import hashlib
import json
from pathlib import Path
from datetime import datetime

DB_FILE = Path("users.json")

def _load_users():
    if not DB_FILE.exists():
        return {}
    return json.loads(DB_FILE.read_text())

def _save_users(users):
    DB_FILE.write_text(json.dumps(users, indent=2))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username: str, password: str) -> tuple[bool, str]:
    users = _load_users()
    if username in users:
        return False, "Username already exists"
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "query_quota": 50
    }
    _save_users(users)
    return True, "Account created successfully"

def login(username: str, password: str) -> tuple[bool, str]:
    users = _load_users()
    if username not in users:
        return False, "Invalid credentials"
    if users[username]["password"] != hash_password(password):
        return False, "Invalid credentials"
    return True, "Login successful"

def get_user_quotas(username: str) -> dict:
    users = _load_users()
    if username not in users:
        return {"query_quota": 0}
    return {
        "query_quota": users[username].get("query_quota", 0)
    }

def decrement_quota(username: str, quota_type: str) -> bool:
    users = _load_users()
    if username not in users:
        return False
    if users[username].get(quota_type, 0) <= 0:
        return False
    users[username][quota_type] -= 1
    _save_users(users)
    return True
