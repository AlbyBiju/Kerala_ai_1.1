from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.document import DocumentOut
from app.schemas.discrepancy import DiscrepancyOut
from app.schemas.checklist import ChecklistItemOut

class ShipmentCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ShipmentSession(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ShipmentDetailOut(ShipmentSession):
    documents: List[DocumentOut] = []
    discrepancies: List[DiscrepancyOut] = []
    checklist_items: List[ChecklistItemOut] = []
