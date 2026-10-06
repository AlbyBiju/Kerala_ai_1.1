import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.discrepancy import Discrepancy
    from app.models.checklist_item import ChecklistItem

class ShipmentSession(Base):
    __tablename__ = "shipment_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    documents: Mapped[List["Document"]] = relationship("Document", back_populates="shipment", cascade="all, delete-orphan", lazy="selectin")
    discrepancies: Mapped[List["Discrepancy"]] = relationship("Discrepancy", back_populates="shipment", cascade="all, delete-orphan", lazy="selectin")
    checklist_items: Mapped[List["ChecklistItem"]] = relationship("ChecklistItem", back_populates="shipment", cascade="all, delete-orphan", lazy="selectin")
