import numpy as np
from sentence_transformers import SentenceTransformer

from hybrid_rag.core.config import settings


class Embedder:
    def __init__(self, model_name: str, query_prompt: str):
        self.model = SentenceTransformer(model_name)
        self.query_prompt = query_prompt

    @property
    def dimension(self) -> int:
        return self.model.get_embedding_dimension()

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)

    def embed_query(self, text: str) -> np.ndarray:
        return self.model.encode(text, prompt=self.query_prompt, normalize_embeddings=True)


embedder = Embedder(settings.embedding_model, settings.query_prompt)
