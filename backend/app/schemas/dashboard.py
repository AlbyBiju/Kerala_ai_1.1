from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime

class RecentSessionSummary(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime

class DashboardResponse(BaseModel):
    total_sessions: int
    open_discrepancies: Dict[str, int]
    overall_pass_rate: float
    recent_sessions: List[RecentSessionSummary]
