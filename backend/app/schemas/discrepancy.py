from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DiscrepancyOut(BaseModel):
    id: str
    shipment_id: str
    field_name: str
    document_a_id: Optional[str] = None
    document_a_value: Optional[str] = None
    document_b_id: Optional[str] = None
    document_b_value: Optional[str] = None
    severity: str  # critical | warning | info
    status: str    # open | acknowledged | resolved
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DiscrepancyStatusUpdate(BaseModel):
    status: str
