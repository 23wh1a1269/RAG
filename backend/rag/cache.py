"""Response caching for query optimization."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
from backend.config import CACHE_DIR

Path(CACHE_DIR).mkdir(exist_ok=True)
CACHE_TTL_HOURS = 24

def _cache_key(question: str, username: str, docs: list) -> str:
    key = f"{question}:{username}:{sorted(docs or [])}"
    return hashlib.md5(key.encode()).hexdigest()

def get_cached(question: str, username: str, docs: list = None) -> Optional[Dict]:
    cache_file = Path(CACHE_DIR) / f"{_cache_key(question, username, docs or [])}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        data = json.loads(cache_file.read_text())
        cached_time = datetime.fromisoformat(data["timestamp"])
        
        if datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS):
            return data["response"]
    except:
        pass
    
    return None

def cache_response(question: str, username: str, docs: list, response: Dict) -> None:
    cache_file = Path(CACHE_DIR) / f"{_cache_key(question, username, docs or [])}.json"
    data = {
        "timestamp": datetime.now().isoformat(),
        "response": response
    }
    cache_file.write_text(json.dumps(data, indent=2))
