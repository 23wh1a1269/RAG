import os
import requests
import sys
from dotenv import load_dotenv

# Load env if exists (we know it doesn't, but for completeness)
load_dotenv()

def check_qdrant():
    print("Checking Qdrant...")
    try:
        r = requests.get("http://localhost:6333/collections", timeout=2)
        if r.status_code == 200:
            print("✅ Qdrant is running")
            return True
        else:
            print(f"❌ Qdrant returned {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Qdrant not reachable: {e}")
        return False

def check_env():
    print("\nChecking Environment...")
    key = os.getenv("GROQ_API_KEY")
    if key and len(key) > 5:
        print("✅ GROQ_API_KEY is set")
        return True
    else:
        print("❌ GROQ_API_KEY is MISSING or empty")
        return False

def test_query():
    print("\nTesting Query Endpoint...")
    try:
        # Simple hello query
        payload = {"question": "Hello", "username": "test_user"}
        r = requests.post("http://localhost:8000/rag/query", json=payload, timeout=10)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"❌ Query Endpoint failed: {e}")

if __name__ == "__main__":
    q_ok = check_qdrant()
    e_ok = check_env()
    
    test_query()
