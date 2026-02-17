from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


class QdrantStorage:
    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection: str = "docs",
        dim: int = 384,
    ):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection

        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=dim,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(self, ids, vectors, payloads):
        points = [
            PointStruct(
                id=ids[i],
                vector=vectors[i],
                payload=payloads[i],
            )
            for i in range(len(ids))
        ]
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k: int = 5, query_filter=None, score_threshold: float = 0.5):
        """Search with score threshold for better relevance."""
        kwargs = {
            "collection_name": self.collection,
            "query_vector": query_vector,
            "with_payload": True,
            "limit": top_k,
            "score_threshold": score_threshold,
        }
        if query_filter:
            kwargs["query_filter"] = query_filter
            
        results = self.client.search(**kwargs)

        contexts, sources, scores = [], set(), []

        for r in results:
            payload = r.payload or {}
            if "text" in payload:
                contexts.append(payload["text"])
                scores.append(r.score)
            if "source" in payload:
                sources.add(payload["source"])

        return {"contexts": contexts, "sources": list(sources), "scores": scores}
