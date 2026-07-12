from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.chunking import split_text_into_chunks
from app.services.document_parser import DocumentParsingError, extract_text


class DocumentProcessingError(Exception):
    """Raised when document processing fails."""


def process_document(document: Document, db: Session) -> int:
    try:
        extracted_text = extract_text(document.file_path)
        chunks = split_text_into_chunks(extracted_text)

        if not chunks:
            raise DocumentProcessingError(
                f"No chunks were generated for document {document.id}"
            )

        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete()

        for chunk in chunks:
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    character_count=chunk.character_count,
                    page_number=None,
                )
            )

        document.upload_status = "processed"

        db.commit()
        db.refresh(document)

        return len(chunks)

    except DocumentParsingError as exc:
        db.rollback()
        document.upload_status = "failed"
        db.add(document)
        db.commit()

        raise DocumentProcessingError(str(exc)) from exc

    except Exception as exc:
        db.rollback()
        raise DocumentProcessingError(
            f"Failed to process document {document.id}"
        ) from exc
