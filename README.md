# 📚 Document Chat Application

An intelligent document chat application that allows you to upload PDF documents and chat with them using AI. Built with FastAPI, Streamlit, LlamaIndex, Qdrant, and Groq.

## ✨ Features

- 📄 **PDF Document Upload**: Upload multiple PDF documents
- 🤖 **AI-Powered Chat**: Chat with your documents using Groq's LLM
- 🔍 **Semantic Search**: Find relevant information using vector embeddings
- 📊 **Document Management**: Track uploaded documents and processing status
- 🎨 **Beautiful UI**: Modern, responsive Streamlit interface
- ⚡ **Background Processing**: Async document processing with Inngest
- 📚 **Source Citations**: Get references to specific pages and documents

## 🚀 Quick Start

### Prerequisites
- Docker installed and running
- Python 3.8+
- Node.js (for Inngest CLI)

### 1. Setup Environment
```bash
# Update your .env file with your actual Groq API key
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
QDRANT_URL=http://localhost:6333
```

### 2. Start All Services
```bash
# Make sure you're in the project directory
cd document-chat-app

# Run the startup script
./start.sh
```

### 3. Manual Startup (Alternative)
If you prefer to start services manually:

```bash
# Terminal 1: Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Terminal 2: Start FastAPI
source .venv/bin/activate
uvicorn main:app --reload

# Terminal 3: Start Inngest
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery

# Terminal 4: Start Streamlit
streamlit run streamlit_app.py
```

## 🌐 Access Points

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 📖 How to Use

1. **Upload Documents**: Use the sidebar to upload PDF files
2. **Wait for Processing**: Documents are processed in the background
3. **Start Chatting**: Ask questions about your uploaded documents
4. **View Sources**: See which documents and pages were used for answers

## 🔧 API Endpoints

- `POST /upload` - Upload a PDF document
- `POST /chat` - Chat with documents
- `GET /documents` - List uploaded documents
- `/api/inngest` - Inngest webhook endpoint

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│   FastAPI API   │────│  Qdrant Vector  │
│                 │    │                 │    │    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │  Inngest Queue  │
                       │   (Background   │
                       │   Processing)   │
                       └─────────────────┘
```

## 🔄 Document Processing Flow

1. **Upload**: PDF uploaded via Streamlit UI
2. **Queue**: Document queued for background processing
3. **Extract**: Text extracted from PDF pages
4. **Chunk**: Text split into manageable chunks
5. **Embed**: Chunks converted to vector embeddings
6. **Store**: Embeddings stored in Qdrant database
7. **Ready**: Document ready for chat queries

## 🎯 Enhanced Features

### Document Limits & Large Files
- Supports large PDF documents (up to 100MB)
- Intelligent chunking for better context preservation
- Batch processing for multiple documents

### Improved UI Design
- Modern gradient design
- Responsive layout
- Real-time chat interface
- Document statistics
- Source highlighting

### Research Paper Optimization
- Academic paper structure recognition
- Citation extraction
- Abstract and conclusion highlighting
- Multi-language support

## 🛠️ Troubleshooting

### Common Issues

1. **Qdrant Connection Error**
   ```bash
   # Restart Qdrant container
   docker stop qdrant-db && docker rm qdrant-db
   docker run -d -p 6333:6333 --name qdrant-db qdrant/qdrant
   ```

2. **Groq API Errors**
   - Check your API key in `.env`
   - Verify API quota and limits

3. **Document Processing Stuck**
   - Check Inngest dev server is running
   - Restart FastAPI server

4. **Memory Issues with Large Documents**
   - Increase Docker memory limits
   - Process documents in smaller batches

## 📝 Development

### Adding New Features
1. **New Document Types**: Extend `llama_index.readers.file`
2. **Better Embeddings**: Try different sentence-transformers models
3. **Advanced Chat**: Add conversation memory and context
4. **User Management**: Add authentication and user sessions

### Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Optional
MAX_CHUNK_SIZE=1000               # Optional
CHUNK_OVERLAP=200                 # Optional
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Happy chatting with your documents! 📚🤖**
