from pathlib import Path
from typing import List
from functools import lru_cache

from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

@lru_cache(maxsize=1)
def get_embedding_model():
    """Cached embedding model to avoid reloading."""
    return SentenceTransformer("all-MiniLM-L6-v2")

embedding_model = get_embedding_model()
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)  # Reduced for better precision


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


def embed_texts(texts: List[str], batch_size: int = 32) -> List[list]:
    """Embed texts with batching for efficiency."""
    embeddings = embedding_model.encode(
        texts, 
        convert_to_numpy=True,
        batch_size=batch_size,
        show_progress_bar=False
    )
    return embeddings.tolist()
