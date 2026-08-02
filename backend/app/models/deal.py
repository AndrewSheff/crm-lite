"""Модель сделки — основная бизнес-сущность CRM."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.tag import deal_tags


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stages.id"), nullable=False
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    probability: Mapped[int] = mapped_column(Integer, default=50)
    expected_close_date = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="medium")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    closed_at = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("probability >= 0 AND probability <= 100", name="ck_deals_probability"),
    )

    # связи
    client = relationship("Client", back_populates="deals", lazy="joined")
    stage = relationship("Stage", lazy="joined")
    owner = relationship("User", lazy="joined")
    tags = relationship("Tag", secondary=deal_tags, lazy="joined")
    notes = relationship("Note", back_populates="deal", lazy="noload")
    activities = relationship("Activity", back_populates="deal", lazy="noload")
