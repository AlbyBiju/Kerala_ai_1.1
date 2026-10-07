import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.document import Document
from app.models.extracted_field import ExtractedField
from app.utils.parsers import parse_document
from app.services.llm import get_llm_provider
from app.services.storage import storage_service
from app.core.fields import CANONICAL_FIELDS_PER_DOC

logger = logging.getLogger(__name__)

class ExtractionService:
    @classmethod
    async def extract_document(cls, document_id: str, db: AsyncSession) -> bool:
        stmt = select(Document).where(Document.id == document_id)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            return False

        try:
            document.extraction_status = "processing"
            await db.commit()

            # 1. Parse document
            parsed_doc = parse_document(storage_service.materialize(document.file_path), document.mime_type)

            # 2. Get expected canonical fields for this document type
            expected_fields = CANONICAL_FIELDS_PER_DOC.get(document.doc_type, [])

            # 3. Call LLM / extraction provider
            llm_provider = get_llm_provider()
            extracted_dict = await llm_provider.extract_fields(
                document_text=parsed_doc.text,
                doc_type=document.doc_type,
                expected_fields=expected_fields
            )

            # 4. Remove previous extracted fields if any
            await db.execute(delete(ExtractedField).where(ExtractedField.document_id == document_id))

            # 5. Persist extracted fields
            for field_name, field_val in extracted_dict.items():
                if field_val and str(field_val).strip():
                    field_record = ExtractedField(
                        document_id=document.id,
                        field_name=field_name,
                        field_value=str(field_val).strip(),
                        confidence_score=0.95,
                        page_number=1
                    )
                    db.add(field_record)

            document.extraction_status = "done"
            await db.commit()
            return True

        except Exception as e:
            logger.exception("Document extraction failed: %s", e)
            await db.rollback()
            document.extraction_status = "failed"
            await db.commit()
            return False
