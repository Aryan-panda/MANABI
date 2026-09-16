import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, ForeignKey, Integer, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base, utc_now


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'preference', 'skill', 'goal', 'academic_fact'
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)   # e.g., 'preferred_programming_language', 'java_proficiency'
    value: Mapped[str] = mapped_column(Text, nullable=False)                  # e.g., 'intermediate'
    confidence: Mapped[str] = mapped_column(String(20), default="low", nullable=False)  # 'low', 'medium', 'high'
    evidence_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="memories")
