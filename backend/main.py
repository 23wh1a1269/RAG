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
from backend.auth import signup, login, verify_token, get_user_profile, update_profile, change_password, request_reset, reset_password, decrement_quota
from backend.email_service import send_welcome_email
from backend.rag.data_loader import load_and_chunk_pdf, embed_texts
from backend.rag.vector_db import QdrantStorage
from backend.rag.prompts import SYSTEM_PROMPT, create_user_prompt, format_response
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
        upload_path = Path(UPLOADS_DIR) / username
        upload_path.mkdir(parents=True, exist_ok=True)
        file_path = upload_path / file.filename
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        chunks = load_and_chunk_pdf(str(file_path.resolve()))
        vectors = embed_texts(chunks)
        
        source_id = f"{username}/{file.filename}"
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"text": chunk, "source": source_id} for chunk in chunks]
        
        QdrantStorage().upsert(ids, vectors, payloads)
        
        return {"success": True, "message": "Upload successful", "data": {"chunks": len(chunks)}}
    except Exception as e:
        return {"success": False, "message": f"Upload failed: {str(e)}"}

# ========== RAG QUERY ==========

@app.post("/rag/query")
async def query_endpoint(req: QueryRequest, username: str = Depends(verify_token)):
    try:
        print(f"\n[DEBUG] Query from {username}: {req.question}")
        print(f"[DEBUG] Selected docs: {req.selected_documents}")
        
        # Check cache
        cached = get_cached(req.question, username, req.selected_documents or [])
        if cached:
            print("[DEBUG] Returning cached response")
            return {"success": True, "data": cached}
        
        # Search vector DB
        store = QdrantStorage()
        query_vector = embed_texts([req.question])[0]
        
        # Adaptive top_k
        search_k = 10 if any(kw in req.question.lower() for kw in ["summarize", "summary", "overview"]) else req.top_k
        found = store.search(query_vector, search_k)
        
        print(f"[DEBUG] Found {len(found['contexts'])} contexts from vector DB")
        print(f"[DEBUG] Sources: {found['sources']}")

        if not found["contexts"]:
            response = {"answer": "No relevant context found.", "sources": [], "num_contexts": 0}
            return {"success": True, "data": response}

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
        
        print(f"[DEBUG] After filtering: {len(filtered_contexts)} contexts")
        print(f"[DEBUG] Filtered sources: {filtered_sources}")
        
        if not filtered_contexts:
            response = {"answer": "No relevant context in selected documents.", "sources": [], "num_contexts": 0}
            return {"success": True, "data": response}

        # Generate answer
        context_limit = 8 if search_k > 5 else 3
        context_block = "\n\n".join(filtered_contexts[:context_limit])
        
        print(f"[DEBUG] Calling Groq AI with {len(filtered_contexts[:context_limit])} contexts")
        
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": create_user_prompt(context_block, req.question)}
            ],
            temperature=0.1,
            max_tokens=512
        )

        answer = format_response(completion.choices[0].message.content.strip())
        
        print(f"[DEBUG] Got answer: {answer[:100]}...")
        
        response = {
            "answer": answer,
            "sources": filtered_sources,
            "num_contexts": len(filtered_contexts)
        }
        
        # Cache and save
        cache_response(req.question, username, req.selected_documents or [], response)
        add_chat(username, req.question, answer, filtered_sources)
        decrement_quota(username, "query_quota")
        
        return {"success": True, "data": response}
        
    except Exception as e:
        print(f"[ERROR] Query failed: {str(e)}")
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
