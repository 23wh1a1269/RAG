"""FastAPI backend for RAG PDF Chat application."""
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

from config import *
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from auth import (
    signup as auth_signup, login as auth_login, get_user_profile,
    update_profile, change_password, request_reset, reset_password
)
from user_data import add_chat, get_chat_history, get_user_documents, delete_user_document
from email_service import send_welcome_email, send_reset_email
from prompts import SYSTEM_PROMPT, create_user_prompt, format_response

app = FastAPI(title="RAG PDF Chat API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== MODELS ==========

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    new_username: str | None = None
    new_email: str | None = None

class QueryRequest(BaseModel):
    question: str
    top_k: int = DEFAULT_TOP_K
    username: str | None = None
    selected_documents: list[str] | None = None  # NEW: Filter by specific documents

# ========== AUTH ENDPOINTS ==========

@app.post("/auth/signup")
async def signup(req: SignupRequest):
    """Create new user account."""
    success, msg = auth_signup(req.username, req.email, req.password)
    if success:
        send_welcome_email(req.email, req.username)
    return {"success": success, "message": msg}

@app.post("/auth/login")
async def login(req: LoginRequest):
    """Authenticate user."""
    success, msg = auth_login(req.username, req.password)
    return {"success": success, "message": msg}

@app.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """Request password reset."""
    success, username, token = request_reset(req.email)
    if success:
        send_reset_email(req.email, username, token)
    return {"success": success, "message": "Reset link sent" if success else "Email not found"}

@app.post("/auth/reset-password")
async def reset_pass(req: ResetPasswordRequest):
    """Reset password with token."""
    success, msg = reset_password(req.token, req.new_password)
    return {"success": success, "message": msg}

@app.post("/auth/change-password")
async def change_pass(req: ChangePasswordRequest):
    """Change user password."""
    success, msg = change_password(req.username, req.old_password, req.new_password)
    return {"success": success, "message": msg}

# ========== PROFILE ENDPOINTS ==========

@app.get("/profile/{username}")
async def get_profile(username: str):
    """Get user profile information."""
    return get_user_profile(username)

@app.put("/profile/{username}")
async def update_prof(username: str, req: UpdateProfileRequest):
    """Update user profile."""
    success, result = update_profile(username, req.new_username, req.new_email)
    return {
        "success": success,
        "message": result if not success else "Updated",
        "username": result if success else username
    }

# ========== DOCUMENT ENDPOINTS ==========

@app.get("/documents/{username}")
async def get_docs(username: str):
    """Get user's uploaded documents."""
    return {"documents": get_user_documents(username)}

@app.delete("/documents/{username}/{doc}")
async def delete_doc(username: str, doc: str):
    """Delete a document."""
    success = delete_user_document(username, doc)
    return {"success": success}

@app.get("/history/{username}")
async def get_history(username: str):
    """Get user's chat history."""
    return {"history": get_chat_history(username)}

# ========== PDF UPLOAD ==========

@app.post("/rag/upload")
async def upload_file(file: UploadFile = File(...), username: str = Form(...)):
    """Upload and process PDF file."""
    # Save file
    upload_path = Path(UPLOADS_DIR) / username
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / file.filename
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Process PDF
    try:
        chunks = load_and_chunk_pdf(str(file_path.resolve()))
        vectors = embed_texts(chunks)
        
        # Create unique IDs
        source_id = f"{username}/{file.filename}"
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"text": chunk, "source": source_id} for chunk in chunks]
        
        # Store in vector DB
        QdrantStorage().upsert(ids, vectors, payloads)
        
        return {"status": "uploaded", "chunks": len(chunks)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ========== RAG QUERY ==========

@app.post("/rag/query")
async def query(req: QueryRequest):
    """Query documents using intelligent RAG assistant."""
    try:
        # Search vector DB with score threshold
        store = QdrantStorage()
        query_vector = embed_texts([req.question])[0]
        
        # Increase top_k for better context coverage on summaries
        search_k = 10 if any(kw in req.question.lower() for kw in 
                            ["summarize", "summary", "overview", "main topics", "explain"]) else req.top_k
        
        found = store.search(query_vector, search_k, score_threshold=0.4)

        if not found["contexts"]:
            return {
                "answer": "No relevant context found in the uploaded documents.",
                "sources": [],
                "num_contexts": 0,
            }

        # Filter by username and selected documents
        if req.username:
            filtered_contexts = []
            filtered_sources = []
            
            for ctx, src in zip(found["contexts"], found["sources"]):
                if not src.startswith(f"{req.username}/"):
                    continue
                
                if req.selected_documents:
                    doc_name = src.split("/", 1)[1] if "/" in src else src
                    if doc_name not in req.selected_documents:
                        continue
                
                filtered_contexts.append(ctx)
                filtered_sources.append(src)
            
            if not filtered_contexts:
                msg = "No relevant context found in the selected documents." if req.selected_documents else "No relevant context found in your uploaded documents."
                return {
                    "answer": msg,
                    "sources": [],
                    "num_contexts": 0,
                }
            
            found["contexts"] = filtered_contexts
            found["sources"] = filtered_sources

        # Use more context for comprehensive questions
        context_limit = 8 if search_k > 5 else 3
        context_block = "\n\n".join(found["contexts"][:context_limit])
        client = Groq(api_key=GROQ_API_KEY)

        # Adjust parameters based on question type
        is_comprehensive = any(kw in req.question.lower() for kw in 
                              ["summarize", "summary", "overview", "explain", "describe"])
        
        completion = client.chat.completions.create(
            model=GROQ_MODELS[0],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": create_user_prompt(context_block, req.question)},
            ],
            temperature=0.2 if is_comprehensive else 0.1,
            max_tokens=1024 if is_comprehensive else 512,
        )

        answer = format_response(completion.choices[0].message.content.strip())

        # Save to history
        if req.username:
            add_chat(req.username, req.question, answer, found["sources"])
            from auth import decrement_quota
            decrement_quota(req.username, "query_quota")

        return {
            "answer": answer,
            "sources": found["sources"],
            "num_contexts": len(found["contexts"]),
        }

    except Exception as e:
        return {
            "answer": "Error processing query. Please try again.",
            "sources": [],
            "num_contexts": 0,
            "error": str(e),
        }

# ========== LEGACY ENDPOINT (Streamlit compatibility) ==========

class IngestRequest(BaseModel):
    pdf_path: str
    source_id: str | None = None

@app.post("/rag/ingest")
async def ingest_http(req: IngestRequest):
    """Legacy endpoint for Streamlit compatibility."""
    try:
        chunks = load_and_chunk_pdf(req.pdf_path)
        vectors = embed_texts(chunks)
        
        source_id = req.source_id or Path(req.pdf_path).name
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"text": chunk, "source": source_id} for chunk in chunks]
        
        QdrantStorage().upsert(ids, vectors, payloads)
        
        return {"status": "ingestion triggered", "chunks": len(chunks)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
