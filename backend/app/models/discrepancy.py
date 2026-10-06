import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.shipment import ShipmentSession

class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("shipment_sessions.id", ondelete="CASCADE"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    document_a_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, default=None)
    document_a_value: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    document_b_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, default=None)
    document_b_value: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)  # critical | warning | info
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)      # open | acknowledged | resolved
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    shipment: Mapped["ShipmentSession"] = relationship("ShipmentSession", back_populates="discrepancies")
