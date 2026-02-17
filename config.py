"""Configuration management for RAG application."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODELS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

# Database
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
USERS_DB_FILE = "users.json"

# Email (Optional)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Paths
UPLOADS_DIR = "uploads"
CHAT_HISTORY_DIR = "chat_history"

# RAG Parameters (Optimized)
DEFAULT_QUERY_QUOTA = 50
DEFAULT_TOP_K = 3  # Reduced for better precision
EMBEDDING_DIM = 384
COLLECTION_NAME = "docs"
CHUNK_SIZE = 512  # Smaller chunks for better retrieval
CHUNK_OVERLAP = 50  # Reduced overlap

# Frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8501"]
