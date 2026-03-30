"""SQLAlchemy model for the ``vrf_lite_extensions`` table (E.20)."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class VrfLiteExtensionDB(UUIDTimestampMixin, Base):
    __tablename__ = "vrf_lite_extensions"
    __table_args__ = (
        UniqueConstraint(
            "fabric_id", "vrf_name", "switch_name", "interface",
            name="uq_vrf_lite_ext",
        ),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    vrf_name: Mapped[str] = mapped_column(String(64), nullable=False)
    switch_name: Mapped[str] = mapped_column(String(64), nullable=False)
    interface: Mapped[str] = mapped_column(String(64), nullable=False)
    ipv4_neighbor: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    ipv6_neighbor: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    peer_vrf: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    dot1q_vlan: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bgp_peer_asn: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
