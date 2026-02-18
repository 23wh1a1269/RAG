# 🚀 RAG PDF Chat Application

A production-ready Retrieval-Augmented Generation (RAG) application that allows users to upload PDFs and chat with them using AI. Built with FastAPI backend and vanilla HTML/CSS/JavaScript frontend.

## ✨ Features

- 🔐 **User Authentication** - Secure signup/login with JWT tokens
- 📄 **PDF Upload & Processing** - Upload multiple PDFs with automatic chunking and embedding
- 💬 **AI-Powered Q&A** - Ask questions and get contextual answers from your documents
- 🎯 **Smart Retrieval** - Vector-based semantic search using Qdrant
- 📊 **Document Management** - View and delete uploaded documents
- 🕒 **Chat History** - Track all your conversations
- 👤 **User Profiles** - Manage account settings and quotas
- 🌓 **Dark/Light Theme** - Toggle between themes
- 📧 **Email Notifications** - Welcome emails and password reset (optional)
- 🔒 **User Isolation** - Each user's data is completely isolated

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser   │─────▶│   FastAPI    │─────▶│   Qdrant    │
│ (HTML/CSS/JS)│◀─────│   Backend    │◀─────│  Vector DB  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Groq LLM    │
                     │ (llama-3.3)  │
                     └──────────────┘
```

## 📁 Project Structure

```
RAG/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Main API endpoints
│   ├── config.py              # Configuration management
│   ├── auth.py                # Authentication & JWT
│   ├── email_service.py       # Email notifications
│   ├── rag/                   # RAG functionality
│   │   ├── data_loader.py     # PDF processing & embeddings
│   │   ├── vector_db.py       # Qdrant vector database
│   │   ├── prompts.py         # LLM prompts
│   │   └── cache.py           # Query caching
│   └── user/                  # User management
│       ├── user_data.py       # User data operations
│       └── admin.py           # Admin utilities
│
├── frontend/                  # HTML/CSS/JS frontend
│   ├── index.html             # Login/Signup page
│   ├── dashboard.html         # Main application
│   ├── reset-password.html    # Password reset page
│   ├── css/
│   │   └── style.css          # All styles
│   └── js/
│       ├── auth.js            # Authentication logic
│       ├── dashboard.js       # Dashboard functionality
│       └── reset.js           # Password reset logic
│
├── uploads/                   # User-uploaded PDFs
├── chat_history/              # Conversation logs
├── cache/                     # Query cache
├── users.json                 # User database
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project metadata
└── start-all.sh              # Startup script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker (for Qdrant)
- Groq API key (free at https://console.groq.com)

### 1. Clone & Setup

```bash
cd /path/to/RAG
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
QDRANT_URL=http://localhost:6333

# Optional - Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Start Qdrant Vector Database

```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

### 4. Run Application

**Option A: Using startup script (recommended)**
```bash
./start-all.sh
```

**Option B: Manual start**
```bash
# Terminal 1 - Backend
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 3000
```

### 5. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Qdrant Dashboard:** http://localhost:6333/dashboard

## 📖 Usage Guide

### First Time Setup

1. Open http://localhost:3000
2. Click **Sign Up** tab
3. Create account with username, email, password
4. Login with your credentials

### Upload & Chat

1. Go to **Chat** tab
2. Click **Upload PDFs** and select files
3. Wait for processing (chunking + embedding)
4. Type your question in the text area
5. Click **Ask AI** to get answers

### Manage Documents

1. Go to **Documents** tab
2. View all uploaded PDFs
3. Delete documents you no longer need

### View History

1. Go to **History** tab
2. Browse past conversations
3. Expand to see full Q&A

### Update Profile

1. Go to **Profile** tab
2. Update username or email
3. Change password securely

## 🔧 Configuration

### User Quotas

Edit `backend/config.py`:

```python
DEFAULT_QUERY_QUOTA = 50      # Queries per user
DEFAULT_UPLOAD_QUOTA = 10     # PDF uploads per user
```

### RAG Parameters

```python
DEFAULT_TOP_K = 3             # Context chunks per query
CHUNK_SIZE = 512              # Characters per chunk
CHUNK_OVERLAP = 50            # Overlap between chunks
EMBEDDING_DIM = 384           # all-MiniLM-L6-v2 dimension
```

### Email Setup (Gmail)

1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password in `.env` file

## 🛠️ API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login and get JWT token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token
- `POST /auth/change-password` - Change password (authenticated)

### Profile
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile

### Documents
- `GET /documents` - List user documents
- `DELETE /documents/{doc}` - Delete document
- `POST /rag/upload` - Upload PDF

### RAG
- `POST /rag/query` - Ask question
- `GET /history` - Get chat history

## 🔒 Security Features

- SHA-256 password hashing
- JWT token authentication
- User data isolation
- CORS protection
- Secure password reset tokens (1-hour expiry)
- Input validation

## 🎨 Frontend Features

- Responsive design
- Dark/Light theme toggle
- Real-time feedback
- Loading states
- Error handling
- Session management
- Clean, modern UI

## 📊 Tech Stack

**Backend:**
- FastAPI - Web framework
- Groq - LLM API (llama-3.3-70b-versatile)
- Qdrant - Vector database
- Sentence Transformers - Embeddings (all-MiniLM-L6-v2)
- LlamaIndex - PDF processing

**Frontend:**
- Vanilla JavaScript (no frameworks)
- HTML5 & CSS3
- Fetch API for HTTP requests

**Storage:**
- JSON file for users
- Qdrant for vectors
- Local filesystem for PDFs

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000
kill -9 <PID>

# Check logs
tail -f backend.log
```

### Qdrant connection error
```bash
# Verify Qdrant is running
curl http://localhost:6333
docker ps | grep qdrant

# Restart Qdrant
docker restart <container_id>
```

### Frontend not loading
```bash
# Check if port 3000 is in use
lsof -i :3000

# Try different port
cd frontend && python3 -m http.server 8080
```

### Email not sending
- Verify SMTP credentials in `.env`
- For Gmail, use App Password (not regular password)
- Check 2FA is enabled on Gmail account

## 🛑 Stop Application

```bash
# Kill processes
pkill -f "uvicorn backend.main"
pkill -f "http.server 3000"

# Or if using start-all.sh
# Press Ctrl+C in terminal
```

## 📝 Development

### Add new endpoint

1. Edit `backend/main.py`
2. Add route with `@app.post()` or `@app.get()`
3. Update frontend JS to call new endpoint

### Modify UI

1. Edit HTML in `frontend/*.html`
2. Update styles in `frontend/css/style.css`
3. Add logic in `frontend/js/*.js`

### Change LLM model

Edit `.env`:
```env
GROQ_MODEL=mixtral-8x7b-32768
# or
GROQ_MODEL=llama-3.1-70b-versatile
```

## 📄 License

MIT License - Feel free to use for personal or commercial projects

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📧 Support

For issues or questions:
- Check troubleshooting section
- Review API docs at http://localhost:8000/docs
- Check Qdrant logs: `docker logs <container_id>`

## 🎯 Roadmap

- [ ] OAuth integration (Google, GitHub)
- [ ] Multi-language support
- [ ] Advanced search filters
- [ ] Document sharing between users
- [ ] Export chat history
- [ ] Mobile responsive improvements
- [ ] Real-time collaboration
- [ ] Custom LLM model support

---

**Built with ❤️ using FastAPI, Groq, and Qdrant**
