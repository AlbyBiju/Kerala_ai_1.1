import re
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from dateutil import parser as date_parser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.shipment import ShipmentSession
from app.models.document import Document
from app.models.extracted_field import ExtractedField
from app.models.discrepancy import Discrepancy
from app.models.checklist_item import ChecklistItem
from app.core.config import settings
from app.core.fields import get_field_severity, DOC_TYPES

NUMERIC_FIELDS = {
    "total_quantity", "total_weight_kg", "total_value_usd",
    "number_of_cartons", "gross_weight_kg", "net_weight_kg"
}

DATE_FIELDS = {"shipment_date", "test_date"}

def clean_numeric(val: str) -> Optional[float]:
    try:
        cleaned = re.sub(r"[^\d.]", "", val)
        if cleaned:
            return float(cleaned)
    except Exception:
        pass
    return None

def normalize_date(val: str) -> Optional[str]:
    try:
        dt = date_parser.parse(val, fuzzy=True)
        if isinstance(dt, tuple):
            dt = dt[0]
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None

def compare_values(field_name: str, val_a: str, val_b: str, tolerance: float = settings.NUMERIC_TOLERANCE) -> bool:
    """
    Returns True if values MATCH within acceptable criteria, False if there is a DISCREPANCY.
    """
    str_a = str(val_a).strip()
    str_b = str(val_b).strip()

    if str_a.lower() == str_b.lower():
        return True

    # Numeric comparison
    if field_name in NUMERIC_FIELDS:
        num_a = clean_numeric(str_a)
        num_b = clean_numeric(str_b)
        if num_a is not None and num_b is not None:
            max_val = max(abs(num_a), abs(num_b))
            if max_val == 0:
                return True
            diff_ratio = abs(num_a - num_b) / max_val
            return diff_ratio <= tolerance
        return False

    # Date comparison
    if field_name in DATE_FIELDS:
        dt_a = normalize_date(str_a)
        dt_b = normalize_date(str_b)
        if dt_a and dt_b:
            return dt_a == dt_b
        return False

    # String comparison
    norm_a = re.sub(r"\s+", " ", str_a).lower()
    norm_b = re.sub(r"\s+", " ", str_b).lower()
    return norm_a == norm_b

class DiscrepancyEngine:
    @classmethod
    async def run(cls, shipment_id: str, db: AsyncSession) -> List[Discrepancy]:
        # 1. Fetch shipment with documents and fields
        stmt = (
            select(ShipmentSession)
            .where(ShipmentSession.id == shipment_id)
        )
        res = await db.execute(stmt)
        shipment = res.scalar_one_or_none()
        if not shipment:
            return []

        doc_stmt = (
            select(Document)
            .where(Document.shipment_id == shipment_id)
        )
        doc_res = await db.execute(doc_stmt)
        documents = doc_res.scalars().all()

        # Build map: doc_id -> {field_name: field_value}
        doc_fields: Dict[str, Dict[str, str]] = {}
        for doc in documents:
            f_stmt = select(ExtractedField).where(ExtractedField.document_id == doc.id)
            f_res = await db.execute(f_stmt)
            fields = f_res.scalars().all()
            doc_fields[doc.id] = {f.field_name: f.field_value for f in fields}

        # Clear existing discrepancies
        await db.execute(delete(Discrepancy).where(Discrepancy.shipment_id == shipment_id))

        new_discrepancies: List[Discrepancy] = []
        doc_ids = list(doc_fields.keys())
        seen_discrepancies: set = set()

        # Pairwise comparison across documents
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                id_a = doc_ids[i]
                id_b = doc_ids[j]
                fields_a = doc_fields[id_a]
                fields_b = doc_fields[id_b]

                shared_fields = set(fields_a.keys()).intersection(set(fields_b.keys()))
                for field_name in shared_fields:
                    val_a = fields_a[field_name]
                    val_b = fields_b[field_name]

                    is_match = compare_values(field_name, val_a, val_b)
                    if not is_match:
                        # Prevent duplicate identical findings when multiple copies of docs are uploaded
                        val_pair = tuple(sorted([str(val_a).strip(), str(val_b).strip()]))
                        pair_key = (field_name, val_pair)
                        if pair_key in seen_discrepancies:
                            continue
                        seen_discrepancies.add(pair_key)

                        severity = get_field_severity(field_name)
                        disc = Discrepancy(
                            shipment_id=shipment_id,
                            field_name=field_name,
                            document_a_id=id_a,
                            document_a_value=val_a,
                            document_b_id=id_b,
                            document_b_value=val_b,
                            severity=severity,
                            status="open"
                        )
                        db.add(disc)
                        new_discrepancies.append(disc)

        # Update shipment status
        shipment.status = "reviewed"
        await db.commit()

        # Generate checklist
        await cls.generate_checklist(shipment_id, db)
        return new_discrepancies

    @classmethod
    async def generate_checklist(cls, shipment_id: str, db: AsyncSession) -> List[ChecklistItem]:
        doc_stmt = select(Document).where(Document.shipment_id == shipment_id)
        doc_res = await db.execute(doc_stmt)
        documents = doc_res.scalars().all()

        disc_stmt = select(Discrepancy).where(Discrepancy.shipment_id == shipment_id)
        disc_res = await db.execute(disc_stmt)
        discrepancies = disc_res.scalars().all()

        # Clear existing checklist items
        await db.execute(delete(ChecklistItem).where(ChecklistItem.shipment_id == shipment_id))

        checklist: List[ChecklistItem] = []

        # Rule 1: All 5 Document Types Present
        present_types = {d.doc_type for d in documents}
        missing_types = set(DOC_TYPES) - present_types
        r1_passed = len(missing_types) == 0
        r1_note = "All 5 standard export documents present." if r1_passed else f"Missing documents: {', '.join(missing_types)}"
        checklist.append(ChecklistItem(
            shipment_id=shipment_id,
            label="All 5 required document types uploaded",
            is_passed=r1_passed,
            notes=r1_note
        ))

        # Rule 2: Extraction Succeeded for all documents
        failed_docs = [d.original_filename for d in documents if d.extraction_status == "failed"]
        r2_passed = len(failed_docs) == 0 and len(documents) > 0
        r2_note = "All documents extracted cleanly." if r2_passed else f"Extraction failed on: {', '.join(failed_docs)}"
        checklist.append(ChecklistItem(
            shipment_id=shipment_id,
            label="All documents successfully parsed and extracted",
            is_passed=r2_passed,
            notes=r2_note
        ))

        # Rule 3: Zero Open Critical Discrepancies
        critical_open = [d for d in discrepancies if d.severity == "critical" and d.status == "open"]
        r3_passed = len(critical_open) == 0
        r3_note = "No critical legal/customs discrepancies detected." if r3_passed else f"Found {len(critical_open)} critical discrepancies."
        checklist.append(ChecklistItem(
            shipment_id=shipment_id,
            label="Zero open critical discrepancies",
            is_passed=r3_passed,
            notes=r3_note
        ))

        # Rule 4: Legal & Customs Field Consistency (HS Code, Ports)
        legal_issues = [d for d in discrepancies if d.field_name in {"hs_code", "port_of_loading", "port_of_discharge"} and d.status == "open"]
        r4_passed = len(legal_issues) == 0
        r4_note = "HS code and ports match across customs filings." if r4_passed else f"Mismatch in {', '.join({d.field_name for d in legal_issues})}"
        checklist.append(ChecklistItem(
            shipment_id=shipment_id,
            label="Legal & customs fields consistent (HS code, Ports)",
            is_passed=r4_passed,
            notes=r4_note
        ))

        # Rule 5: Quantities and Weights Reconciled
        qty_issues = [d for d in discrepancies if d.field_name in {"total_quantity", "total_weight_kg", "number_of_cartons"} and d.status == "open"]
        r5_passed = len(qty_issues) == 0
        r5_note = "Quantities and cargo weights fully reconciled." if r5_passed else f"Discrepancies in cargo metrics: {', '.join({d.field_name for d in qty_issues})}"
        checklist.append(ChecklistItem(
            shipment_id=shipment_id,
            label="Cargo quantities and weights fully reconciled",
            is_passed=r5_passed,
            notes=r5_note
        ))

        for item in checklist:
            db.add(item)
        await db.commit()
        return checklist
