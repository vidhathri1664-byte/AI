from pathlib import Path

import faiss
import numpy as np

from app.config import BASE_DIR, settings


class VectorStoreError(Exception):
    """Raised when a vector index operation fails."""


def get_index_path() -> Path:
    index_path = BASE_DIR / settings.vector_store_path
    index_path.parent.mkdir(parents=True, exist_ok=True)
    return index_path


def create_index(dimension: int) -> faiss.Index:
    if dimension <= 0:
        raise VectorStoreError(
            "Embedding dimension must be greater than zero"
        )

    base_index = faiss.IndexFlatIP(dimension)
    return faiss.IndexIDMap2(base_index)


def save_index(index: faiss.Index) -> None:
    try:
        faiss.write_index(index, str(get_index_path()))
    except Exception as exc:
        raise VectorStoreError(
            "Failed to save the FAISS index"
        ) from exc


def load_index() -> faiss.Index:
    index_path = get_index_path()

    if not index_path.exists():
        raise VectorStoreError(
            f"FAISS index does not exist: {index_path}"
        )

    try:
        return faiss.read_index(str(index_path))
    except Exception as exc:
        raise VectorStoreError(
            "Failed to load the FAISS index"
        ) from exc


def build_index(
    embeddings: list[list[float]],
    chunk_ids: list[int],
) -> faiss.Index:
    if not embeddings:
        raise VectorStoreError("No embeddings were provided")

    if len(embeddings) != len(chunk_ids):
        raise VectorStoreError(
            "Embedding count must match chunk ID count"
        )

    vectors = np.asarray(embeddings, dtype=np.float32)
    ids = np.asarray(chunk_ids, dtype=np.int64)

    index = create_index(vectors.shape[1])
    index.add_with_ids(vectors, ids)
    save_index(index)

    return index

def search_index(
    query_embedding: list[float],
    top_k: int = 5,
) -> list[tuple[int, float]]:
    if top_k <= 0:
        raise VectorStoreError(
            "top_k must be greater than zero"
        )

    index = load_index()

    query_vector = np.asarray(
        [query_embedding],
        dtype=np.float32,
    )

    if query_vector.shape[1] != index.d:
        raise VectorStoreError(
            "Query dimension does not match index dimension"
        )

    result_count = min(top_k, index.ntotal)

    if result_count == 0:
        return []

    scores, ids = index.search(
        query_vector,
        result_count,
    )

    return [
        (int(chunk_id), float(score))
        for chunk_id, score in zip(ids[0], scores[0])
        if chunk_id != -1
    ]
