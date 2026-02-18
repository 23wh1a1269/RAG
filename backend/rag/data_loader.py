"""PDF loading and embedding."""
from pathlib import Path
from typing import List
from functools import lru_cache
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from sentence_transformers import SentenceTransformer
from backend.config import *

@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

def load_and_chunk_pdf(path: str) -> List[str]:
    pdf_path = Path(path)
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Invalid PDF path")
    
    docs = PDFReader().load_data(file=str(pdf_path))
    chunks = []
    for doc in docs:
        if doc.text:
            chunks.extend(splitter.split_text(doc.text))
    return chunks

def embed_texts(texts: List[str]) -> List[list]:
    embeddings = get_model().encode(texts, convert_to_numpy=True, batch_size=32, show_progress_bar=False)
    return embeddings.tolist()
