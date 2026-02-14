import json
from pathlib import Path
import sys

DB_FILE = Path("users.json")

def load_users():
    if not DB_FILE.exists():
        return {}
    return json.loads(DB_FILE.read_text())

def save_users(users):
    DB_FILE.write_text(json.dumps(users, indent=2))

def list_users():
    users = load_users()
    print("\n=== USER LIST ===")
    for username, data in users.items():
        print(f"\nUsername: {username}")
        print(f"  Upload Quota: {data.get('upload_quota', 0)}")
        print(f"  Query Quota: {data.get('query_quota', 0)}")
        print(f"  Created: {data.get('created_at', 'N/A')}")

def update_quota(username: str, quota_type: str, amount: int):
    users = load_users()
    if username not in users:
        print(f"User '{username}' not found")
        return
    users[username][quota_type] = amount
    save_users(users)
    print(f"Updated {username}'s {quota_type} to {amount}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python admin.py list")
        print("  python admin.py quota <username> <upload_quota|query_quota> <amount>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        list_users()
    elif cmd == "quota" and len(sys.argv) == 5:
        update_quota(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        print("Invalid command")
