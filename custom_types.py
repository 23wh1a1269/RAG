from typing import List, Optional
from pydantic import BaseModel


class RAGChunkAndSrc(BaseModel):
    chunks: List[str]
    source_id: Optional[str] = None


class RAGUpsertResult(BaseModel):
    ingested: int


class RAGSearchResult(BaseModel):
    contexts: List[str]
    sources: List[str]


class RAGQueryResult(BaseModel):
    answer: str
    sources: List[str]
    num_contexts: int