# RAG PDF Chat Application

A production-ready Retrieval-Augmented Generation (RAG) application with user authentication, quota management, and modern UI.

## ✨ Features

### Core RAG Functionality
- PDF document ingestion with chunking and embedding
- Semantic search using Qdrant vector database
- AI-powered question answering with Groq LLM
- Source citation and context display

### User Management
- 🔐 Secure authentication (signup/login/logout)
- 👤 User-specific document storage
- 📊 Per-user upload and query quotas
- 🕒 Persistent chat history per user

### Modern UI/UX
- 🎨 Beautiful gradient design with animations
- 📱 Responsive layout with tabs
- 💬 Real-time quota indicators
- 🚀 Smooth transitions and micro-interactions

### Document Management
- 📚 View all uploaded documents
- 🗑️ Delete documents
- 📄 User-isolated storage

## 🏗️ Architecture

```
RAG/
├── main.py              # FastAPI backend with Inngest workflows
├── streamlit_app.py     # Enhanced Streamlit UI with auth
├── data_loader.py       # PDF loading and embedding
├── vector_db.py         # Qdrant vector storage
├── custom_types.py      # Pydantic models
├── auth.py              # NEW: Authentication system
├── user_data.py         # NEW: User data & history management
├── ui_styles.py         # NEW: Custom CSS styling
├── admin.py             # NEW: Admin utility
├── uploads/             # User-specific document storage
│   └── <username>/
├── chat_history/        # User chat history
├── users.json           # User database
└── qdrant_storage/      # Vector database
```

## 🚀 Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
# or with uv:
uv sync
```

2. **Configure environment (.env):**
```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
QDRANT_URL=http://localhost:6333
```

3. **Start Qdrant (if not running):**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

4. **Start backend:**
```bash
uvicorn main:app --reload
```

5. **Start Streamlit UI:**
```bash
streamlit run streamlit_app.py
```

## 📖 Usage

### User Flow
1. **Sign up** with username and password
2. **Login** to access the application
3. **Upload PDFs** (uses upload quota)
4. **Ask questions** about documents (uses query quota)
5. **View chat history** and manage documents

### Default Quotas
- Upload quota: 10 documents per user
- Query quota: 50 queries per user

### Admin Management
```bash
# List all users and their quotas
python admin.py list

# Update user quota
python admin.py quota <username> upload_quota 20
python admin.py quota <username> query_quota 100
```

## 🎨 UI Features

- **Gradient backgrounds** with smooth animations
- **Quota badges** showing remaining usage
- **Tab-based navigation** for different features
- **Chat history** with expandable conversations
- **Document management** with delete functionality
- **Responsive design** that works on all screen sizes

## 🔒 Security

- Passwords hashed with SHA-256
- User-isolated document storage
- Session-based authentication
- No sensitive data in frontend

## 🛠️ New Files Added

1. **auth.py** - User authentication and quota management
2. **user_data.py** - Chat history and document tracking
3. **ui_styles.py** - Custom CSS for modern UI
4. **admin.py** - Admin utility for user management

## 📝 Design Decisions

### Why These Enhancements?

1. **Authentication**: Essential for multi-user production apps
2. **Quotas**: Prevent abuse and manage API costs
3. **User Isolation**: Each user only sees their own documents
4. **Chat History**: Users can review past conversations
5. **Modern UI**: Improves user engagement and experience

### Backward Compatibility

- All existing files preserved
- Original functionality intact
- New features are additive only
- No breaking changes to core RAG pipeline

## 🔮 Future Enhancements

1. **Advanced Features**
   - Multi-document comparison
   - Export chat history to PDF
   - Document sharing between users
   - Advanced search filters

2. **Performance**
   - Caching layer for frequent queries
   - Async document processing
   - Batch upload support

3. **Analytics**
   - Usage statistics dashboard
   - Popular queries tracking
   - Document analytics

4. **Security**
   - OAuth integration
   - Two-factor authentication
   - Role-based access control

## 📄 License

MIT License - Feel free to use and modify!