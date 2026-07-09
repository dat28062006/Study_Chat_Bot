from fastembed import TextEmbedding

class EmbeddingService:
    def __init__(self):
        # Chay model local, khong can mang
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def embed(self, text: str) -> list[float]:
        # fastembed tra ve generator chua numpy arrays
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = list(self.model.embed(texts))
        return [emb.tolist() for emb in embeddings]

embedding_service = EmbeddingService()
