from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingGenerationError(Exception):
    """Raised when local embedding generation fails."""


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    try:
        return SentenceTransformer(settings.embedding_model)
    except Exception as exc:
        raise EmbeddingGenerationError(
            "Failed to load the local embedding model"
        ) from exc


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    cleaned_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not cleaned_texts:
        raise EmbeddingGenerationError(
            "At least one non-empty text is required"
        )

    try:
        model = get_embedding_model()

        vectors = model.encode(
            cleaned_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return vectors.tolist()

    except EmbeddingGenerationError:
        raise

    except Exception as exc:
        raise EmbeddingGenerationError(
            "Failed to generate local embeddings"
        ) from exc


def generate_embedding(text: str) -> list[float]:
    return generate_embeddings([text])[0]
