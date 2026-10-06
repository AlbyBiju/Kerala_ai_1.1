import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.shipment import ShipmentSession
    from app.models.extracted_field import ExtractedField

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("shipment_sessions.id", ondelete="CASCADE"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extraction_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    shipment: Mapped["ShipmentSession"] = relationship("ShipmentSession", back_populates="documents")
    extracted_fields: Mapped[List["ExtractedField"]] = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan", lazy="selectin")
