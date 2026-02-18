"""Admin utility for user management."""
import sys
import json
from pathlib import Path

DB_FILE = Path("users.json")

def load_users():
    return json.loads(DB_FILE.read_text()) if DB_FILE.exists() else {}

def save_users(users):
    DB_FILE.write_text(json.dumps(users, indent=2))

def list_users():
    users = load_users()
    print(f"\n{'Username':<20} {'Email':<30} {'Query Quota':<15}")
    print("-" * 65)
    for username, data in users.items():
        print(f"{username:<20} {data.get('email', 'N/A'):<30} {data.get('query_quota', 0):<15}")

def update_quota(username, quota_type, value):
    users = load_users()
    if username not in users:
        print(f"User '{username}' not found")
        return
    
    users[username][quota_type] = int(value)
    save_users(users)
    print(f"Updated {username}'s {quota_type} to {value}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python admin.py [list|quota <username> <type> <value>]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "list":
        list_users()
    elif cmd == "quota" and len(sys.argv) == 5:
        update_quota(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Invalid command")
