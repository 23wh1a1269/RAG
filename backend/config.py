"""Production configuration management."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

# Database
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
USERS_DB_FILE = "users.json"

# Email
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Paths
UPLOADS_DIR = "uploads"
CHAT_HISTORY_DIR = "chat_history"
CACHE_DIR = "cache"

# RAG Parameters
DEFAULT_QUERY_QUOTA = 50
DEFAULT_TOP_K = 3
EMBEDDING_DIM = 384
COLLECTION_NAME = "docs"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
SCORE_THRESHOLD = 0.4

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
