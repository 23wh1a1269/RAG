"""User data and history management."""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from backend.config import *

Path(CHAT_HISTORY_DIR).mkdir(exist_ok=True)

def _history_file(username: str) -> Path:
    return Path(CHAT_HISTORY_DIR) / f"{username}.json"

def _load_history(username: str) -> List[Dict]:
    file = _history_file(username)
    return json.loads(file.read_text()) if file.exists() else []

def _save_history(username: str, history: List[Dict]):
    _history_file(username).write_text(json.dumps(history, indent=2))

def add_chat(username: str, question: str, answer: str, sources: List[str]):
    history = _load_history(username)
    history.append({
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "sources": sources
    })
    _save_history(username, history)

def get_chat_history(username: str) -> List[Dict]:
    return _load_history(username)

def get_user_documents(username: str) -> List[str]:
    uploads = Path(UPLOADS_DIR) / username
    return [f.name for f in uploads.glob("*.pdf")] if uploads.exists() else []

def delete_user_document(username: str, filename: str) -> bool:
    file_path = Path(UPLOADS_DIR) / username / filename
    if file_path.exists():
        file_path.unlink()
        return True
    return False
