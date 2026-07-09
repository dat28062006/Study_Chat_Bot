import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import settings

COLLECTION_NAME = "documents"
VECTOR_SIZE = 384


class VectorService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self._ensure_collection()

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )

    def upsert(self, document_id: str, chunks: list[str], embeddings: list[list[float]]):
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "document_id": document_id,
                        "chunk_index": i,
                    },
                )
            )

        batch_size = 100
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=points[i : i + batch_size],
            )

    def search(
        self,
        query_embedding: list[float],
        document_ids: list[str] | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        query_filter = None
        if document_ids:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchAny(any=document_ids),
                    )
                ]
            )

        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter,
        )

        return [
            {
                "text": hit.payload["text"],
                "document_id": hit.payload["document_id"],
                "score": hit.score,
            }
            for hit in results
        ]

    def delete_by_document(self, document_id: str):
        self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )


vector_service = VectorService()
