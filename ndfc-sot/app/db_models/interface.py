"""SQLAlchemy model for the ``interfaces`` table (E.5).

Single table with ``type`` discriminator + JSONB ``type_config`` for
type-specific fields.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class InterfaceDB(UUIDTimestampMixin, Base):
    __tablename__ = "interfaces"
    __table_args__ = (
        UniqueConstraint("switch_id", "name", name="uq_interface_switch_name"),
    )

    switch_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("switches.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)

    # Common fields shared by all interface types
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    admin_state: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=True
    )
    mtu: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    speed: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Type-specific fields stored as JSONB
    type_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
