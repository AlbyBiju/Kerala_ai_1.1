from typing import Optional
from pydantic import BaseModel, ConfigDict

class ChecklistItemOut(BaseModel):
    id: str
    shipment_id: str
    label: str
    is_passed: bool
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
