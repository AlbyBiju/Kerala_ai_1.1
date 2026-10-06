from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ExtractedFieldOut(BaseModel):
    id: str
    document_id: str
    field_name: str
    field_value: str
    confidence_score: float
    page_number: int

    model_config = ConfigDict(from_attributes=True)

class DocumentOut(BaseModel):
    id: str
    shipment_id: str
    doc_type: str
    original_filename: str
    mime_type: str
    extraction_status: str
    created_at: datetime
    extracted_fields: Optional[List[ExtractedFieldOut]] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentUploadResponse(BaseModel):
    id: str
    doc_type: str
    original_filename: str
    extraction_status: str
