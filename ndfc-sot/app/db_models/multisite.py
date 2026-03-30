"""SQLAlchemy model for the ``multisite_configs`` table (E.3)."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class MultisiteDB(UUIDTimestampMixin, Base):
    __tablename__ = "multisite_configs"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_multisite_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    enabled: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    multisite_bgw_ip: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    dci_subnet_range: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    dci_subnet_mask: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    delay_restore: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=300
    )
