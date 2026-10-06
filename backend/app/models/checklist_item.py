import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.shipment import ShipmentSession

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("shipment_sessions.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    is_passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    shipment: Mapped["ShipmentSession"] = relationship("ShipmentSession", back_populates="checklist_items")
