"""Vector database operations."""
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from backend.config import *

class QdrantStorage:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL, timeout=30)
        self.collection = COLLECTION_NAME

        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
            )

    def upsert(self, ids, vectors, payloads):
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k: int = DEFAULT_TOP_K, score_threshold: float = SCORE_THRESHOLD):
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            with_payload=True,
            limit=top_k,
            score_threshold=score_threshold
        )

        contexts, sources = [], set()
        for r in results:
            if r.payload and "text" in r.payload:
                contexts.append(r.payload["text"])
            if r.payload and "source" in r.payload:
                sources.add(r.payload["source"])

        return {"contexts": contexts, "sources": list(sources)}
