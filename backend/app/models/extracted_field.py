import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.document import Document

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    field_value: Mapped[str] = mapped_column(String(1024), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="extracted_fields")
