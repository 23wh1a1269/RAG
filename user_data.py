import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

HISTORY_DIR = Path("chat_history")
HISTORY_DIR.mkdir(exist_ok=True)

def _get_user_file(username: str) -> Path:
    return HISTORY_DIR / f"{username}.json"

def _load_history(username: str) -> List[Dict]:
    file = _get_user_file(username)
    if not file.exists():
        return []
    return json.loads(file.read_text())

def _save_history(username: str, history: List[Dict]):
    file = _get_user_file(username)
    file.write_text(json.dumps(history, indent=2))

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
    uploads = Path("uploads") / username
    if not uploads.exists():
        return []
    return [f.name for f in uploads.glob("*.pdf")]

def delete_user_document(username: str, filename: str) -> bool:
    file_path = Path("uploads") / username / filename
    if file_path.exists():
        file_path.unlink()
        return True
    return False
