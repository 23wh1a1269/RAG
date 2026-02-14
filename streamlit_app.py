import time
import requests
from pathlib import Path
import streamlit as st
from auth import signup, login, get_user_quotas, decrement_quota
from user_data import add_chat, get_chat_history, get_user_documents, delete_user_document
from ui_styles import get_custom_css

st.set_page_config(page_title="RAG PDF Chat", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

def save_uploaded_pdf(file, username: str) -> Path:
    uploads = Path("uploads") / username
    uploads.mkdir(parents=True, exist_ok=True)
    path = uploads / file.name
    path.write_bytes(file.getbuffer())
    return path

# -------- AUTHENTICATION --------
if not st.session_state.logged_in:
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">🚀 RAG PDF Chat</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Chat with your documents using AI-powered intelligence</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 Login", "✨ Sign Up"])
        
        with tab1:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            login_user = st.text_input("Username", key="login_user", placeholder="Enter your username")
            login_pass = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            
            if st.button("Login →", key="login_btn", use_container_width=True):
                success, msg = login(login_user, login_pass)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.rerun()
                else:
                    st.error(msg)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            signup_user = st.text_input("Username", key="signup_user", placeholder="Choose a username")
            signup_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="Create a password")
            signup_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2", placeholder="Confirm your password")
            
            if st.button("Create Account →", key="signup_btn", use_container_width=True):
                if signup_pass != signup_pass2:
                    st.error("Passwords don't match")
                elif len(signup_pass) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, msg = signup(signup_user, signup_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -------- MAIN APP (LOGGED IN) --------
username = st.session_state.username
quotas = get_user_quotas(username)

# Header
st.markdown(f'''
<div class="dashboard-header">
    <div class="header-content">
        <h1 class="dashboard-title">Welcome back, {username}! 👋</h1>
        <p class="dashboard-subtitle">Manage your documents and chat with AI</p>
    </div>
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-value">∞</div>
            <div class="stat-label">Uploads</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{quotas["query_quota"]}</div>
            <div class="stat-label">Queries Left</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Logout", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# -------- TABS --------
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📚 Documents", "🕒 History"])

with tab1:
    col_left, col_right = st.columns([2, 3])
    
    with col_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF files", 
            type=["pdf"], 
            accept_multiple_files=True,
            key="pdf_uploader",
            help="Upload one or more PDF files to chat with"
        )
        
        upload_btn = st.button("📤 Upload", key="upload_btn", use_container_width=True, disabled=not uploaded_files)
        
        if upload_btn and uploaded_files:
            with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
                success_count = 0
                for uploaded in uploaded_files:
                    path = save_uploaded_pdf(uploaded, username)
                    r = requests.post(
                        "http://localhost:8000/rag/ingest",
                        json={"pdf_path": str(path.resolve()), "source_id": f"{username}/{path.name}"},
                        timeout=60,
                    )
                    if r.status_code == 200:
                        success_count += 1
                
                if success_count > 0:
                    st.success(f"✅ Successfully uploaded {success_count} file(s)!")
                else:
                    st.error("❌ Failed to upload files")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 💬 Ask Questions")
        question = st.text_area(
            "Your question", 
            key="question_input", 
            placeholder="What would you like to know about your documents?",
            height=100
        )
        
        col_k, col_btn = st.columns([1, 1])
        with col_k:
            top_k = st.slider("Context chunks", 1, 10, 5, key="top_k_query")
        with col_btn:
            ask_btn = st.button("🚀 Ask AI", type="primary", key="ask_button", use_container_width=True)
        
        if ask_btn and question.strip():
            if quotas["query_quota"] <= 0:
                st.error("❌ Query quota exhausted!")
            else:
                with st.spinner("🤔 AI is thinking..."):
                    r = requests.post(
                        "http://localhost:8000/rag/query",
                        json={"question": question, "top_k": top_k, "username": username},
                        timeout=120,
                    )
                    
                    if r.status_code != 200:
                        st.error("❌ Backend error")
                        st.code(r.text)
                    else:
                        result = r.json()
                        decrement_quota(username, "query_quota")
                        
                        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                        st.markdown("#### 🧠 Answer")
                        st.write(result.get("answer", "No answer returned"))
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        if result.get("sources"):
                            with st.expander("📄 View Sources"):
                                for s in result["sources"]:
                                    st.markdown(f"- `{s}`")
                        
                        add_chat(username, question, result.get("answer", ""), result.get("sources", []))
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📚 Your Document Library")
    docs = get_user_documents(username)
    
    if not docs:
        st.info("📭 No documents uploaded yet. Upload your first PDF to get started!")
    else:
        st.markdown(f"**Total Documents:** {len(docs)}")
        st.markdown('<div class="documents-grid">', unsafe_allow_html=True)
        for doc in docs:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f'<div class="doc-item">📄 {doc}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"del_{doc}", help="Delete document"):
                    if delete_user_document(username, doc):
                        st.success(f"Deleted {doc}")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🕒 Conversation History")
    history = get_chat_history(username)
    
    if not history:
        st.info("💭 No chat history yet. Start asking questions!")
    else:
        st.markdown(f"**Total Conversations:** {len(history)}")
        for i, chat in enumerate(reversed(history[-20:])):
            with st.expander(f"💬 {chat['question'][:60]}... • {chat['timestamp'][:10]}"):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['answer']}")
                if chat.get('sources'):
                    st.markdown(f"**Sources:** {', '.join(chat['sources'])}")
    st.markdown('</div>', unsafe_allow_html=True)
