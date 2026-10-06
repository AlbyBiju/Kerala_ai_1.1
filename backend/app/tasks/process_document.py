from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.document import Document
from app.services.extraction import ExtractionService
from app.services.discrepancy import DiscrepancyEngine

async def process_document_task(document_id: str, shipment_id: str):
    async with async_session_maker() as db:
        # Extract document
        await ExtractionService.extract_document(document_id, db)

        # Check if all documents for this shipment are done
        stmt = select(Document).where(Document.shipment_id == shipment_id)
        res = await db.execute(stmt)
        docs = res.scalars().all()

        all_done = all(d.extraction_status in {"done", "failed"} for d in docs)
        if all_done and len(docs) > 0:
            await DiscrepancyEngine.run(shipment_id, db)

async def run_analysis_task(shipment_id: str):
    async with async_session_maker() as db:
        # Extract any pending documents first
        stmt = select(Document).where(Document.shipment_id == shipment_id)
        res = await db.execute(stmt)
        docs = res.scalars().all()

        for d in docs:
            if d.extraction_status == "pending":
                await ExtractionService.extract_document(d.id, db)

        await DiscrepancyEngine.run(shipment_id, db)
