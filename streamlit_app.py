import streamlit as st
import requests
import json
from typing import List

# Page config
st.set_page_config(
    page_title="📚 Document Chat Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for maximum clarity and visual appeal
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main .block-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 25px;
        padding: 2rem;
        margin: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 3px solid #ff6b35;
        letter-spacing: 2px;
    }
    
    /* Chat messages */
    .chat-message {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #ff6b35;
        backdrop-filter: blur(10px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .user-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 8px solid #4facfe;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        margin-left: 10%;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 8px solid #43e97b;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        margin-right: 10%;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        border: 3px solid #667eea;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        font-weight: 700;
    }
    
    /* Stats cards */
    .stats-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 3px solid #fcb69f;
        font-weight: 700;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    /* Document cards */
    .document-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border: 2px solid #667eea;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .doc-icon {
        font-size: 1.5rem;
        background: rgba(255,255,255,0.2);
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .doc-info {
        flex: 1;
    }
    
    .doc-name {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    
    .doc-stats {
        font-size: 0.8rem;
        opacity: 0.9;
    }
    
    /* Dashboard grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-item {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #1a1a1a;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid #43e97b;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .stat-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    
    .stat-label {
        font-size: 0.8rem;
        font-weight: 600;
        opacity: 0.8;
    }
    
    /* Home page styles */
    .home-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .home-hero h2 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    
    .home-hero p {
        font-size: 1.3rem;
        opacity: 0.9;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #1a1a1a;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border: 3px solid #43e97b;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-card h3 {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .feature-card p {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    .steps-container {
        display: flex;
        gap: 2rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .step-item {
        flex: 1;
        min-width: 250px;
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 15px;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        border: 2px solid #fa709a;
    }
    
    .step-number {
        background: rgba(255,255,255,0.3);
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .step-content h4 {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .step-content p {
        font-size: 0.9rem;
        opacity: 0.8;
        margin: 0;
    }
    
    /* Source boxes */
    .source-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #1a1a1a;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 2px solid #fa709a;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
    }
    
    /* Text styling */
    .stMarkdown {
        color: white !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        font-weight: 700 !important;
    }
    
    p, div, span, label {
        color: white !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 12px 35px rgba(0,0,0,0.4) !important;
        background: linear-gradient(135deg, #f7931e 0%, #ff6b35 100%) !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        border: 3px dashed #ff6b35 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stFileUploader label {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Input styling */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255,255,255,0.1) !important;
        border: 2px solid #4facfe !important;
        border-radius: 15px !important;
        color: white !important;
        backdrop-filter: blur(10px) !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ff6b35 !important;
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.3) !important;
    }
    
    /* Success/Error/Info messages */
    .stSuccess {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        color: #1a1a1a !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        border: 2px solid #43e97b !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        border: 2px solid #ff6b6b !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        border: 2px solid #4facfe !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #f7931e 0%, #ff6b35 100%);
    }
</style>
""", unsafe_allow_html=True)

# API endpoints
API_BASE = "http://localhost:8000"

def upload_document(file):
    """Upload document to the API"""
    files = {"file": (file.name, file.getvalue(), "application/pdf")}
    response = requests.post(f"{API_BASE}/upload", files=files)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

def chat_with_documents(question: str):
    """Send chat request to API"""
    response = requests.post(
        f"{API_BASE}/chat",
        json={"question": question}
    )
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

def get_documents():
    """Get list of uploaded documents"""
    try:
        response = requests.get(f"{API_BASE}/documents")
        return response.json()
    except:
        return {"documents": []}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Navigation
st.sidebar.markdown("## 🧭 Navigation")
page = st.sidebar.selectbox("Go to:", ["Home", "Chat with Documents"], index=0 if st.session_state.current_page == "Home" else 1)
st.session_state.current_page = page

if page == "Home":
    # Home Page
    st.markdown('<h1 class="main-header">📚 Document Chat Assistant</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="home-hero">
        <h2>🚀 Welcome to Your AI Document Assistant</h2>
        <p>Upload PDF documents and chat with them using advanced AI technology!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <h3>Upload PDFs</h3>
            <p>Upload multiple PDF documents and process them automatically</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>AI Chat</h3>
            <p>Ask questions and get intelligent answers from your documents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📖</div>
            <h3>Source Citations</h3>
            <p>Get exact page references for all answers and information</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works
    st.markdown("## 🔧 How It Works")
    st.markdown("""
    <div class="steps-container">
        <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-content">
                <h4>Upload Documents</h4>
                <p>Upload your PDF files using the sidebar</p>
            </div>
        </div>
        <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
                <h4>Processing</h4>
                <p>AI processes and indexes your documents</p>
            </div>
        </div>
        <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-content">
                <h4>Chat & Ask</h4>
                <p>Ask questions and get instant answers</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get started button
    st.markdown("## 🎯 Ready to Start?")
    if st.button("🚀 Go to Chat", type="primary"):
        st.session_state.current_page = "Chat with Documents"
        st.rerun()

else:
    # Chat Page (existing content)
    st.markdown('<h1 class="main-header">📚 Document Chat Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Upload documents and chat with them using AI! 🤖✨")

# Sidebar
with st.sidebar:
    st.markdown("## 📁 Document Management")
    
    # Upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload New Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload research papers, reports, or any PDF document"
    )
    
    if uploaded_file is not None:
        if st.button("🚀 Upload & Process", type="primary"):
            with st.spinner("Uploading and processing document..."):
                try:
                    result = upload_document(uploaded_file)
                    st.success(f"✅ {result['message']}")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error uploading document: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Document list
    st.markdown("### 📋 Uploaded Documents")
    docs_data = get_documents()
    
    if docs_data["documents"]:
        for doc in docs_data["documents"]:
            st.markdown(f"""
            <div class="document-card">
                <div class="doc-icon">📄</div>
                <div class="doc-info">
                    <div class="doc-name">{doc['filename']}</div>
                    <div class="doc-stats">✅ {doc['chunks']} chunks ready</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No documents uploaded yet. Upload your first document to get started!")
    
    # Stats
    st.markdown("### 📊 Dashboard")
    st.markdown(f"""
    <div class="dashboard-grid">
        <div class="stat-item">
            <div class="stat-icon">💬</div>
            <div class="stat-value">{len(st.session_state.messages)}</div>
            <div class="stat-label">Messages</div>
        </div>
        <div class="stat-item">
            <div class="stat-icon">📚</div>
            <div class="stat-value">{len(docs_data["documents"])}</div>
            <div class="stat-label">Documents</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main chat interface
st.markdown("## 💬 Chat with Your Documents")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>🧑‍💼 You:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)
        
        # Show sources if available
        if "sources" in message and message["sources"]:
            st.markdown("**📚 Sources:**")
            for source in message["sources"]:
                st.markdown(f"""
                <div class="source-box">
                    📖 {source}
                </div>
                """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    st.markdown(f"""
    <div class="chat-message user-message">
        <strong>🧑‍💼 You:</strong><br>
        {prompt}
    </div>
    """, unsafe_allow_html=True)
    
    # Get AI response
    with st.spinner("🤔 Thinking..."):
        try:
            response = chat_with_documents(prompt)
            
            # Add assistant message
            assistant_message = {
                "role": "assistant", 
                "content": response["answer"],
                "sources": response["sources"]
            }
            st.session_state.messages.append(assistant_message)
            
            # Display assistant response
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong><br>
                {response["answer"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources
            if response["sources"]:
                st.markdown("**📚 Sources:**")
                for source in response["sources"]:
                    st.markdown(f"""
                    <div class="source-box">
                        📖 {source}
                    </div>
                    """, unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"❌ Error getting response: {str(e)}")
            st.info("💡 Make sure the FastAPI server is running and you have uploaded some documents!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🚀 Built with FastAPI, Streamlit, LlamaIndex, and Groq</p>
    <p>💡 Upload PDFs and start chatting with your documents!</p>
</div>
""", unsafe_allow_html=True)

# Clear chat button
if st.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()
