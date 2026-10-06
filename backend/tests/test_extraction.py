"""Sub-Task 6 tests: extraction service with a mocked LLM provider."""
import pytest
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.document import Document
from app.models.extracted_field import ExtractedField
from app.services import extraction as extraction_module
from app.services.extraction import ExtractionService


class MockLLMProvider:
    """Deterministic stand-in for the OpenAI/watsonx providers."""

    async def extract_fields(self, document_text: str, doc_type: str, expected_fields: list) -> dict:
        return {
            "exporter_name": "Mock Exporter Ltd.",
            "total_quantity": "1200",
            "hs_code": "0306.17.00",
        }


@pytest.mark.asyncio
async def test_extraction_persists_fields_and_status():
    # Create a document row directly
    async with async_session_maker() as db:
        document = Document(
            shipment_id="00000000-0000-0000-0000-000000000001",
            doc_type="commercial_invoice",
            original_filename="mock.pdf",
            file_path="mock.pdf",
            mime_type="application/pdf",
            extraction_status="pending",
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        document_id = document.id

    original_provider = extraction_module.get_llm_provider
    extraction_module.get_llm_provider = lambda: MockLLMProvider()
    try:
        async with async_session_maker() as db:
            result = await ExtractionService.extract_document(document_id, db)
            assert result is True

            fields = (
                await db.execute(select(ExtractedField).where(ExtractedField.document_id == document_id))
            ).scalars().all()
            field_names = {f.field_name for f in fields}
            assert {"exporter_name", "total_quantity", "hs_code"}.issubset(field_names)

            doc = (await db.execute(select(Document).where(Document.id == document_id))).scalar_one()
            assert doc.extraction_status == "done"
    finally:
        extraction_module.get_llm_provider = original_provider

    # Cleanup
    async with async_session_maker() as db:
        doc = (await db.execute(select(Document).where(Document.id == document_id))).scalar_one_or_none()
        if doc:
            await db.delete(doc)
            await db.commit()
