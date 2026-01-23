import time
import requests
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="RAG PDF Chat", page_icon="📄")


def save_uploaded_pdf(file) -> Path:
    uploads = Path("uploads")
    uploads.mkdir(exist_ok=True)
    path = uploads / file.name
    path.write_bytes(file.getbuffer())
    return path


st.title("📄 RAG PDF Chat")

# -------- PDF UPLOAD --------
uploaded = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded:
    with st.spinner("Uploading and ingesting PDF..."):
        path = save_uploaded_pdf(uploaded)
        r = requests.post(
            "http://localhost:8000/rag/ingest",
            json={"pdf_path": str(path.resolve()), "source_id": path.name},
            timeout=60,
        )

        if r.status_code == 200:
            st.success("PDF ingestion triggered!")
        else:
            st.error("Failed to ingest PDF")

        time.sleep(0.5)

st.divider()

# -------- QUERY --------
question = st.text_input(
    "Ask a question about the uploaded PDFs",
    key="question_input",
)

top_k = st.number_input(
    "Top K",
    min_value=1,
    max_value=20,
    value=5,
    key="top_k_query",
)

if st.button("Ask", type="primary", key="ask_button") and question.strip():
    with st.spinner("Thinking..."):
        r = requests.post(
            "http://localhost:8000/rag/query",
            json={"question": question, "top_k": top_k},
            timeout=120,
        )

        if r.status_code != 200:
            st.error("❌ Backend error")
            st.code(r.text)
        else:
            result = r.json()

            st.subheader("🧠 Answer")
            st.write(result.get("answer", "No answer returned"))

            if result.get("sources"):
                with st.expander("📄 Sources"):
                    for s in result["sources"]:
                        st.write(f"- {s}")

            if "error" in result:
                st.warning("Backend error details")
                st.code(result["error"])
