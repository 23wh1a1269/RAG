"""Production FastAPI backend with JWT authentication."""
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq

from backend.config import *
from backend.auth import signup, login, verify_token, get_user_profile, update_profile, change_password, request_reset, reset_password
from backend.email_service import send_welcome_email
from backend.rag.data_loader import load_and_chunk_pdf, embed_texts
from backend.rag.vector_db import QdrantStorage
from backend.rag.cache import get_cached, cache_response
from backend.user.user_data import add_chat, get_chat_history, get_user_documents, delete_user_document

app = FastAPI(title="RAG PDF Chat API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

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
    old_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    new_username: str | None = None
    new_email: str | None = None

class QueryRequest(BaseModel):
    question: str
    top_k: int = DEFAULT_TOP_K
    selected_documents: list[str] | None = None

# ========== AUTH ENDPOINTS ==========

@app.post("/auth/signup")
async def signup_endpoint(req: SignupRequest):
    try:
        success, msg = signup(req.username, req.email, req.password)
        if success:
            send_welcome_email(req.email, req.username)
        return {"success": success, "message": msg}
    except Exception as e:
        return {"success": False, "message": "Signup failed"}

@app.post("/auth/login")
async def login_endpoint(req: LoginRequest):
    try:
        success, msg, token = login(req.username, req.password)
        return {"success": success, "message": msg, "data": {"token": token} if success else None}
    except Exception as e:
        return {"success": False, "message": "Login failed"}

@app.post("/auth/forgot-password")
async def forgot_password_endpoint(req: ForgotPasswordRequest):
    try:
        success, msg = request_reset(req.email)
        return {"success": success, "message": msg}
    except Exception as e:
        return {"success": False, "message": "Request failed"}

@app.post("/auth/reset-password")
async def reset_password_endpoint(req: ResetPasswordRequest):
    try:
        success, msg = reset_password(req.token, req.new_password)
        return {"success": success, "message": msg}
    except Exception as e:
        return {"success": False, "message": "Reset failed"}

@app.post("/auth/change-password")
async def change_password_endpoint(req: ChangePasswordRequest, username: str = Depends(verify_token)):
    try:
        success, msg = change_password(username, req.old_password, req.new_password)
        return {"success": success, "message": msg}
    except Exception as e:
        return {"success": False, "message": "Change failed"}

# ========== PROFILE ENDPOINTS ==========

@app.get("/profile")
async def get_profile_endpoint(username: str = Depends(verify_token)):
    try:
        profile = get_user_profile(username)
        return {"success": True, "data": profile}
    except Exception as e:
        return {"success": False, "message": "Failed to fetch profile"}

@app.put("/profile")
async def update_profile_endpoint(req: UpdateProfileRequest, username: str = Depends(verify_token)):
    try:
        success, result = update_profile(username, req.new_username, req.new_email)
        return {
            "success": success,
            "message": result if not success else "Profile updated",
            "data": {"username": result} if success else None
        }
    except Exception as e:
        return {"success": False, "message": "Update failed"}

# ========== DOCUMENT ENDPOINTS ==========

@app.get("/documents")
async def get_documents_endpoint(username: str = Depends(verify_token)):
    try:
        docs = get_user_documents(username)
        return {"success": True, "data": {"documents": docs}}
    except Exception as e:
        return {"success": False, "message": "Failed to fetch documents"}

@app.delete("/documents/{doc}")
async def delete_document_endpoint(doc: str, username: str = Depends(verify_token)):
    try:
        success = delete_user_document(username, doc)
        return {"success": success, "message": "Document deleted" if success else "Delete failed"}
    except Exception as e:
        return {"success": False, "message": "Delete failed"}

@app.get("/history")
async def get_history_endpoint(username: str = Depends(verify_token)):
    try:
        history = get_chat_history(username)
        return {"success": True, "data": {"history": history}}
    except Exception as e:
        return {"success": False, "message": "Failed to fetch history"}

# ========== PDF UPLOAD ==========

@app.post("/rag/upload")
async def upload_endpoint(file: UploadFile = File(...), username: str = Depends(verify_token)):
    try:
        print(f"\n[UPLOAD] User: {username}, File: {file.filename}")
        
        # Validate PDF
        if not file.filename.lower().endswith('.pdf'):
            return {"success": False, "message": "Only PDF files allowed"}
        
        upload_path = Path(UPLOADS_DIR) / username
        upload_path.mkdir(parents=True, exist_ok=True)
        file_path = upload_path / file.filename
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        print(f"[UPLOAD] Saved to: {file_path}")
        
        # Process PDF
        chunks = load_and_chunk_pdf(str(file_path.resolve()))
        print(f"[UPLOAD] Chunked into {len(chunks)} pieces")
        
        if not chunks:
            return {"success": False, "message": "PDF appears to be empty"}
        
        # Generate embeddings
        vectors = embed_texts(chunks)
        print(f"[UPLOAD] Generated {len(vectors)} embeddings")
        
        # Store in Qdrant
        source_id = f"{username}/{file.filename}"
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"text": chunk, "source": source_id} for chunk in chunks]
        
        QdrantStorage().upsert(ids, vectors, payloads)
        print(f"[UPLOAD] Stored in Qdrant with source: {source_id}")
        
        return {"success": True, "message": "Upload successful", "data": {"chunks": len(chunks)}}
    except Exception as e:
        print(f"[UPLOAD ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Upload failed: {str(e)}"}

# ========== RAG QUERY ==========

@app.post("/rag/query")
async def query_endpoint(req: QueryRequest, username: str = Depends(verify_token)):
    try:
        from backend.rag.prompts import (
            DOCUMENT_SYSTEM_PROMPT, GENERAL_SYSTEM_PROMPT, CONVERSATIONAL_PROMPT, SUMMARY_SYSTEM_PROMPT,
            create_document_prompt, create_general_prompt, create_conversational_prompt, create_summary_prompt,
            format_response, is_conversational, is_summary_request
        )
        from backend.config import MIN_CONTEXT_CHUNKS, FALLBACK_THRESHOLD
        
        print(f"\n[QUERY] User: {username}, Question: {req.question}")
        
        # Handle conversational queries
        if is_conversational(req.question):
            print("[QUERY] Detected conversational query")
            client = Groq(api_key=GROQ_API_KEY)
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": CONVERSATIONAL_PROMPT},
                    {"role": "user", "content": create_conversational_prompt(req.question)}
                ],
                temperature=0.3,
                max_tokens=150
            )
            answer = format_response(completion.choices[0].message.content.strip())
            response = {"answer": answer, "sources": [], "num_contexts": 0, "mode": "conversational"}
            return {"success": True, "data": response}
        
        # Detect summary request BEFORE retrieval
        if is_summary_request(req.question):
            print("[QUERY] Detected FULL DOCUMENT SUMMARY request")
            
            # Get ALL chunks for user's documents (or selected documents)
            store = QdrantStorage()
            
            # Retrieve many chunks (no semantic search, just get document content)
            # Use a dummy vector to get all user's documents
            from backend.rag.data_loader import get_model
            dummy_query = "document content"
            query_vector = get_model().encode([dummy_query], convert_to_numpy=True)[0].tolist()
            
            # Get up to 50 chunks (adjust based on token limits)
            found = store.search(query_vector, top_k=50, score_threshold=0.0)  # No threshold, get all
            
            # Filter by username and selected documents
            filtered_contexts, filtered_sources = [], []
            for ctx, src in zip(found["contexts"], found["sources"]):
                if not src.startswith(f"{username}/"):
                    continue
                if req.selected_documents:
                    doc_name = src.split("/", 1)[1] if "/" in src else src
                    if doc_name not in req.selected_documents:
                        continue
                filtered_contexts.append(ctx)
                filtered_sources.append(src)
            
            print(f"[QUERY] SUMMARY MODE: Retrieved {len(filtered_contexts)} chunks")
            
            if not filtered_contexts:
                # User has no documents uploaded
                return {
                    "success": True,
                    "data": {
                        "answer": "No documents have been uploaded yet. Please upload a PDF to get a summary.",
                        "sources": [],
                        "num_contexts": 0,
                        "mode": "summary_no_docs"
                    }
                }
            
            # Combine chunks (token-safe: limit to ~3000 tokens = ~12000 chars)
            combined_content = "\n\n".join(filtered_contexts[:30])  # ~30 chunks max
            
            client = Groq(api_key=GROQ_API_KEY)
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": create_summary_prompt(combined_content)}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            answer = format_response(completion.choices[0].message.content.strip())
            response = {
                "answer": answer,
                "sources": list(set(filtered_sources)),
                "num_contexts": len(filtered_contexts),
                "mode": "full_document_summary"
            }
            
            # Cache and save
            cache_response(req.question, username, req.selected_documents or [], response)
            add_chat(username, req.question, answer, response["sources"])
            
            return {"success": True, "data": response}
        
        # Regular semantic search for specific questions
        # Check cache
        cached = get_cached(req.question, username, req.selected_documents or [])
        if cached:
            print("[QUERY] Returning cached response")
            return {"success": True, "data": cached}
        
        # Search vector DB
        store = QdrantStorage()
        query_vector = embed_texts([req.question])[0]
        
        # Use configured top_k
        found = store.search(query_vector, req.top_k, score_threshold=0.25)
        
        print(f"[QUERY] Found {len(found['contexts'])} contexts, best score: {found.get('best_score', 0):.3f}")

        # Filter by username and selected documents
        filtered_contexts, filtered_sources, filtered_scores = [], [], []
        for i, (ctx, src) in enumerate(zip(found["contexts"], found["sources"])):
            if not src.startswith(f"{username}/"):
                continue
            if req.selected_documents:
                doc_name = src.split("/", 1)[1] if "/" in src else src
                if doc_name not in req.selected_documents:
                    continue
            filtered_contexts.append(ctx)
            filtered_sources.append(src)
            if i < len(found.get("scores", [])):
                filtered_scores.append(found["scores"][i])
        
        print(f"[QUERY] After filtering: {len(filtered_contexts)} contexts")
        
        # Determine if we have confident context
        has_confident_context = (
            len(filtered_contexts) >= MIN_CONTEXT_CHUNKS and
            (filtered_scores and max(filtered_scores) >= FALLBACK_THRESHOLD)
        )
        
        client = Groq(api_key=GROQ_API_KEY)
        
        if has_confident_context:
            # Use document-based answering
            print(f"[QUERY] Using DOCUMENT mode (score: {max(filtered_scores):.3f})")
            context_limit = min(8, len(filtered_contexts))
            context_block = "\n\n".join(filtered_contexts[:context_limit])
            
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": DOCUMENT_SYSTEM_PROMPT},
                    {"role": "user", "content": create_document_prompt(context_block, req.question)}
                ],
                temperature=0.15,
                max_tokens=600
            )
            
            answer = format_response(completion.choices[0].message.content.strip())
            response = {
                "answer": answer,
                "sources": list(set(filtered_sources[:context_limit])),
                "num_contexts": context_limit,
                "mode": "document",
                "confidence": max(filtered_scores)
            }
            
        else:
            # Use general knowledge fallback ONLY when no chunks AND not summary request
            print(f"[QUERY] Using GENERAL KNOWLEDGE mode (low/no context)")
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
                    {"role": "user", "content": create_general_prompt(req.question)}
                ],
                temperature=0.2,
                max_tokens=400
            )
            
            answer = format_response(completion.choices[0].message.content.strip())
            response = {
                "answer": answer,
                "sources": [],
                "num_contexts": 0,
                "mode": "general_knowledge",
                "confidence": 0.0
            }
        
        print(f"[QUERY] Mode: {response['mode']}, Answer length: {len(answer)} chars")
        
        # Cache and save
        cache_response(req.question, username, req.selected_documents or [], response)
        add_chat(username, req.question, answer, response.get("sources", []))
        
        return {"success": True, "data": response}
        
    except Exception as e:
        print(f"[QUERY ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Query failed: {str(e)}"}


# ========== FRONTEND ROUTES ==========

@app.get("/")
async def root():
    """Serve login page."""
    return FileResponse("frontend/index.html")

@app.get("/dashboard")
async def dashboard():
    """Serve dashboard page."""
    return FileResponse("frontend/dashboard.html")

@app.get("/reset-password")
async def reset_password_page():
    """Serve password reset page."""
    return FileResponse("frontend/reset-password.html")
