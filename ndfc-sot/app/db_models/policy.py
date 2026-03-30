"""SQLAlchemy models for policies, policy groups, and assignments (E.22/E.23)."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class PolicyDB(UUIDTimestampMixin, Base):
    """E.22 — Individual policy applied to a switch."""

    __tablename__ = "policies"
    __table_args__ = (
        UniqueConstraint(
            "fabric_id", "switch_name", "template_name",
            name="uq_policy_fabric_switch_tpl",
        ),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    switch_name: Mapped[str] = mapped_column(String(64), nullable=False)
    template_name: Mapped[str] = mapped_column(String(128), nullable=False)
    priority: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=500
    )
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PolicyGroupDB(UUIDTimestampMixin, Base):
    """E.23 — Policy group with embedded policies and switch list."""

    __tablename__ = "policy_groups"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_policy_group_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    policies: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    switches: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
