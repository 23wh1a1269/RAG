import time
import requests
from pathlib import Path
import streamlit as st
from auth import (signup, login, get_user_quotas, decrement_quota, 
                  get_user_profile, update_profile, change_password,
                  request_reset, reset_password)
from user_data import add_chat, get_chat_history, get_user_documents, delete_user_document
from theme import get_theme_css
from email_service import send_welcome_email, send_reset_email

st.set_page_config(page_title="RAG PDF Chat", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Apply theme
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

def save_uploaded_pdf(file, username: str) -> Path:
    uploads = Path("uploads") / username
    uploads.mkdir(parents=True, exist_ok=True)
    path = uploads / file.name
    path.write_bytes(file.getbuffer())
    return path

# Check for password reset token
query_params = st.query_params
if "reset_token" in query_params and not st.session_state.logged_in:
    st.markdown('<div class="center-wrapper">', unsafe_allow_html=True)
    st.markdown('<h1 class="app-title">🔒 Reset Password</h1>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card auth-width">', unsafe_allow_html=True)
    
    new_pass = st.text_input("New Password", type="password", key="reset_pass")
    new_pass2 = st.text_input("Confirm Password", type="password", key="reset_pass2")
    
    if st.button("Reset Password", use_container_width=True):
        if new_pass != new_pass2:
            st.error("Passwords don't match")
        elif len(new_pass) < 6:
            st.error("Password must be at least 6 characters")
        else:
            success, msg = reset_password(query_params["reset_token"], new_pass)
            if success:
                st.success(msg)
                st.query_params.clear()
                time.sleep(2)
                st.rerun()
            else:
                st.error(msg)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# -------- AUTHENTICATION --------
if not st.session_state.logged_in:
    st.markdown('<div class="center-wrapper">', unsafe_allow_html=True)
    st.markdown('<h1 class="app-title">🚀 RAG PDF Chat</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Chat with your PDFs using intelligent retrieval‑augmented AI</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Login", "Create Account", "Forgot Password"])

    with tab1:
        st.markdown('<div class="glass-card auth-width">', unsafe_allow_html=True)
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn", use_container_width=True):
            success, msg = login(login_user, login_pass)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.rerun()
            else:
                st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card auth-width">', unsafe_allow_html=True)
        signup_user = st.text_input("Username", key="signup_user")
        signup_email = st.text_input("Email", key="signup_email")
        signup_pass = st.text_input("Password", type="password", key="signup_pass")
        signup_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2")

        if st.button("Create Account", key="signup_btn", use_container_width=True):
            if signup_pass != signup_pass2:
                st.error("Passwords don't match")
            elif len(signup_pass) < 6:
                st.error("Password must be at least 6 characters")
            elif "@" not in signup_email:
                st.error("Invalid email")
            else:
                success, msg = signup(signup_user, signup_email, signup_pass)
                if success:
                    st.success(msg)
                    send_welcome_email(signup_email, signup_user)
                else:
                    st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="glass-card auth-width">', unsafe_allow_html=True)
        reset_email = st.text_input("Email", key="reset_email")
        
        if st.button("Send Reset Link", key="reset_btn", use_container_width=True):
            success, username, token = request_reset(reset_email)
            if success:
                send_reset_email(reset_email, username, token)
                st.success("Reset link sent to your email")
            else:
                st.error("Email not found")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -------- MAIN APP --------
username = st.session_state.username
quotas = get_user_quotas(username)

# Theme toggle
col_theme, _ = st.columns([1, 10])
with col_theme:
    if st.button("🌓" if st.session_state.theme == "dark" else "☀️", key="theme_toggle"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# Header
st.markdown(f"""
<div class="top-bar">
    <div>
        <div class="welcome">Welcome back</div>
        <div class="username">{username}</div>
    </div>
    <div class="quota-box">
        <div class="quota-label">Queries left</div>
        <div class="quota-value">{quotas['query_quota']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

col_logout, _ = st.columns([1, 6])
with col_logout:
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# -------- TABS --------
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📄 Documents", "🕒 History", "👤 Profile"])

# -------- CHAT TAB --------
with tab1:
    left, right = st.columns([2, 3])

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Upload PDFs")
        uploaded_files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True)

        if st.button("Upload Files", use_container_width=True, disabled=not uploaded_files):
            with st.spinner("Processing files..."):
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
                if success_count:
                    st.success(f"Uploaded {success_count} file(s)")
                else:
                    st.error("Upload failed")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Ask your documents")
        question = st.text_area("Your question", height=120, placeholder="Ask anything from your PDFs...")
        top_k = st.slider("Context chunks", 1, 10, 5)

        if st.button("Ask AI", type="primary", use_container_width=True) and question.strip():
            if quotas["query_quota"] <= 0:
                st.error("Query quota exhausted")
            else:
                with st.spinner("Thinking..."):
                    r = requests.post(
                        "http://localhost:8000/rag/query",
                        json={"question": question, "top_k": top_k, "username": username},
                        timeout=120,
                    )
                    if r.status_code != 200:
                        st.error("Backend error")
                    else:
                        result = r.json()
                        decrement_quota(username, "query_quota")
                        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                        st.markdown(result.get("answer", "No answer returned"))
                        st.markdown('</div>', unsafe_allow_html=True)
                        if result.get("sources"):
                            with st.expander("Sources"):
                                for s in result["sources"]:
                                    st.write(s)
                        add_chat(username, question, result.get("answer", ""), result.get("sources", []))
        st.markdown('</div>', unsafe_allow_html=True)

# -------- DOCUMENTS TAB --------
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Your documents")
    docs = get_user_documents(username)
    if not docs:
        st.info("No documents uploaded yet")
    else:
        for doc in docs:
            c1, c2 = st.columns([6, 1])
            with c1:
                st.write(f"📄 {doc}")
            with c2:
                if st.button("Delete", key=f"del_{doc}"):
                    if delete_user_document(username, doc):
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -------- HISTORY TAB --------
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Conversation history")
    history = get_chat_history(username)
    if not history:
        st.info("No conversations yet")
    else:
        for chat in reversed(history[-20:]):
            with st.expander(chat['question'][:60]):
                st.write("**Question:**", chat['question'])
                st.write("**Answer:**", chat['answer'])
    st.markdown('</div>', unsafe_allow_html=True)

# -------- PROFILE TAB --------
with tab4:
    profile = get_user_profile(username)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown("### Profile Information")
        st.markdown(f'<div class="profile-label">USERNAME</div><div class="profile-value">{profile["username"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">EMAIL</div><div class="profile-value">{profile["email"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">MEMBER SINCE</div><div class="profile-value">{profile["created_at"][:10]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-label">QUERY QUOTA</div><div class="profile-value">{profile["query_quota"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown("### Update Profile")
        new_username = st.text_input("New Username", value=profile["username"], key="new_username")
        new_email = st.text_input("New Email", value=profile["email"], key="new_email")
        
        if st.button("Update Profile", use_container_width=True):
            success, result = update_profile(username, new_username, new_email)
            if success:
                st.success("Profile updated")
                if result != username:
                    st.session_state.username = result
                time.sleep(1)
                st.rerun()
            else:
                st.error(result)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown("### Change Password")
        old_pass = st.text_input("Current Password", type="password", key="old_pass")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        new_pass2 = st.text_input("Confirm New Password", type="password", key="new_pass2")
        
        if st.button("Change Password", use_container_width=True):
            if new_pass != new_pass2:
                st.error("Passwords don't match")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, msg = change_password(username, old_pass, new_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
