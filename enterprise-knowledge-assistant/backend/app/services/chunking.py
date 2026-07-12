from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    content: str
    character_count: int


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[TextChunk]:
    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    normalized_text = " ".join(text.split())

    chunks: list[TextChunk] = []
    start = 0
    chunk_index = 0
    text_length = len(normalized_text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        if end < text_length:
            boundary = normalized_text.rfind(" ", start, end)

            if boundary > start:
                end = boundary

        content = normalized_text[start:end].strip()

        if content:
            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    content=content,
                    character_count=len(content),
                )
            )
            chunk_index += 1

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks
