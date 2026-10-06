from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.core.deps import get_current_session
from app.models.shipment import ShipmentSession
from app.models.document import Document
from app.models.discrepancy import Discrepancy
from app.models.checklist_item import ChecklistItem
from app.schemas.shipment import ShipmentCreate, ShipmentSession as ShipmentSessionSchema, ShipmentDetailOut
from app.schemas.document import DocumentOut, DocumentUploadResponse
from app.schemas.discrepancy import DiscrepancyOut, DiscrepancyStatusUpdate
from app.schemas.checklist import ChecklistItemOut
from app.services.storage import storage_service
from app.services.report import generate_report_content
from app.tasks.process_document import process_document_task, run_analysis_task

router = APIRouter(prefix="/shipments", tags=["Shipments"], dependencies=[Depends(get_current_session)])

@router.post("", response_model=ShipmentSessionSchema, status_code=status.HTTP_201_CREATED)
async def create_shipment(payload: ShipmentCreate, db: AsyncSession = Depends(get_db)):
    shipment = ShipmentSession(
        name=payload.name,
        description=payload.description,
        status="draft"
    )
    db.add(shipment)
    await db.commit()
    await db.refresh(shipment)
    return shipment

@router.get("", response_model=List[ShipmentSessionSchema])
async def list_shipments(db: AsyncSession = Depends(get_db)):
    stmt = select(ShipmentSession).order_by(desc(ShipmentSession.created_at))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{id}", response_model=ShipmentDetailOut)
async def get_shipment(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ShipmentSession).where(ShipmentSession.id == id)
    res = await db.execute(stmt)
    shipment = res.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment session not found")
    return shipment

@router.post("/{id}/documents", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify shipment session exists
    stmt = select(ShipmentSession).where(ShipmentSession.id == id)
    res = await db.execute(stmt)
    shipment = res.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment session not found")

    saved_path, mime_type, file_size = await storage_service.save_file(file)

    document = Document(
        shipment_id=id,
        doc_type=doc_type,
        original_filename=file.filename or "unknown",
        file_path=saved_path,
        mime_type=mime_type,
        file_size_bytes=file_size,
        extraction_status="pending"
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Immediately perform extraction so status updates to done right away
    try:
        from app.services.extraction import ExtractionService
        await ExtractionService.extract_document(document.id, db)
        await db.refresh(document)
    except Exception:
        background_tasks.add_task(process_document_task, document.id, id)

    return DocumentUploadResponse(
        id=document.id,
        doc_type=document.doc_type,
        original_filename=document.original_filename,
        extraction_status=document.extraction_status
    )

@router.get("/{id}/documents", response_model=List[DocumentOut])
async def list_documents(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Document).where(Document.shipment_id == id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/{id}/analyse", status_code=status.HTTP_202_ACCEPTED)
async def analyse_shipment(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ShipmentSession).where(ShipmentSession.id == id)
    res = await db.execute(stmt)
    shipment = res.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment session not found")

    # Perform analysis directly so results are immediately available to the client
    await run_analysis_task(id)
    return {"detail": "Analysis completed"}

@router.post("/{id}/load-samples")
async def load_sample_documents(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ShipmentSession).where(ShipmentSession.id == id)
    res = await db.execute(stmt)
    shipment = res.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment session not found")

    import os
    import shutil
    from app.services.extraction import ExtractionService
    from app.core.config import settings

    fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "docs", "fixtures")
    sample_files = [
        ("invoice.pdf", "commercial_invoice"),
        ("packing_list.pdf", "packing_list"),
        ("shipping_bill.pdf", "shipping_bill"),
        ("purchase_order.pdf", "purchase_order"),
        ("quality_certificate.pdf", "quality_certificate"),
    ]

    # Remove previous documents for this shipment so repeated clicks replace rather than duplicate
    existing_docs = (await db.execute(select(Document).where(Document.shipment_id == id))).scalars().all()
    for d in existing_docs:
        await db.delete(d)
    await db.commit()

    loaded_docs = []
    for fname, dtype in sample_files:
        src = os.path.join(fixtures_dir, fname)
        if os.path.exists(src):
            dst = os.path.join(settings.UPLOAD_DIR, f"sample_{fname}")
            shutil.copyfile(src, dst)
            doc = Document(
                shipment_id=id,
                doc_type=dtype,
                original_filename=fname,
                file_path=dst,
                mime_type="application/pdf",
                file_size_bytes=os.path.getsize(dst),
                extraction_status="pending"
            )
            db.add(doc)
            await db.commit()
            await db.refresh(doc)
            await ExtractionService.extract_document(doc.id, db)
            loaded_docs.append(fname)

    # Run discrepancy engine
    await run_analysis_task(id)
    return {"detail": f"Loaded and analyzed {len(loaded_docs)} sample documents", "documents": loaded_docs}

@router.get("/{id}/discrepancies", response_model=List[DiscrepancyOut])
async def list_discrepancies(
    id: str,
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Discrepancy).where(Discrepancy.shipment_id == id)
    if severity:
        query = query.where(Discrepancy.severity == severity)
    if status_filter:
        query = query.where(Discrepancy.status == status_filter)

    res = await db.execute(query)
    return res.scalars().all()

@router.patch("/{id}/discrepancies/{disc_id}", response_model=DiscrepancyOut)
async def update_discrepancy(
    id: str,
    disc_id: str,
    payload: DiscrepancyStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Discrepancy).where(Discrepancy.id == disc_id, Discrepancy.shipment_id == id)
    res = await db.execute(stmt)
    disc = res.scalar_one_or_none()
    if not disc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discrepancy not found")

    disc.status = payload.status
    await db.commit()
    await db.refresh(disc)
    return disc

@router.get("/{id}/checklist", response_model=List[ChecklistItemOut])
async def get_checklist(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ChecklistItem).where(ChecklistItem.shipment_id == id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{id}/report/pdf")
async def download_report_pdf(id: str, db: AsyncSession = Depends(get_db)):
    try:
        html_out, report_bytes = await generate_report_content(id, db)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment session not found")

    # If binary is PDF (magic bytes %PDF), return application/pdf
    is_pdf = report_bytes.startswith(b"%PDF")
    media_type = "application/pdf" if is_pdf else "text/html; charset=utf-8"
    filename = f"report-{id}.pdf" if is_pdf else f"report-{id}.html"

    return Response(
        content=report_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
