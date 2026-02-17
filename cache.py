"""Response caching for improved query performance."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL_HOURS = 24

def _get_cache_key(question: str, username: str, docs: list) -> str:
    """Generate cache key from query parameters."""
    key_data = f"{question}:{username}:{sorted(docs or [])}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_cached_response(question: str, username: str, docs: list = None) -> Optional[Dict]:
    """Retrieve cached response if valid."""
    cache_key = _get_cache_key(question, username, docs or [])
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        data = json.loads(cache_file.read_text())
        cached_time = datetime.fromisoformat(data["timestamp"])
        
        # Check if cache is still valid
        if datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS):
            return data["response"]
    except:
        pass
    
    return None

def cache_response(question: str, username: str, docs: list, response: Dict) -> None:
    """Cache query response."""
    cache_key = _get_cache_key(question, username, docs or [])
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "response": response
    }
    
    cache_file.write_text(json.dumps(data, indent=2))

def clear_cache() -> int:
    """Clear all cached responses."""
    count = 0
    for cache_file in CACHE_DIR.glob("*.json"):
        cache_file.unlink()
        count += 1
    return count
