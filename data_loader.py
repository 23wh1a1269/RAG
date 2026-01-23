from pathlib import Path
from typing import List

from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)


def load_and_chunk_pdf(path: str) -> List[str]:
    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Path does not exist: {pdf_path}")

    if pdf_path.is_dir():
        raise ValueError("Expected a PDF file, got directory")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")

    docs = PDFReader().load_data(file=str(pdf_path))
    texts = [d.text for d in docs if d.text]

    chunks: List[str] = []
    for text in texts:
        chunks.extend(splitter.split_text(text))

    return chunks


def embed_texts(texts: List[str]) -> List[list]:
    embeddings = embedding_model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()
