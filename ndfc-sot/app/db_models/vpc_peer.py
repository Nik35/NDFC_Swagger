"""SQLAlchemy model for the ``vpc_peers`` table (E.6)."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class VpcPeerDB(UUIDTimestampMixin, Base):
    __tablename__ = "vpc_peers"
    __table_args__ = (
        UniqueConstraint("fabric_id", "peer1", "peer2", name="uq_vpc_peer_pair"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    peer1: Mapped[str] = mapped_column(String(64), nullable=False)
    peer2: Mapped[str] = mapped_column(String(64), nullable=False)
    domain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    peer_link_po_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    peer_link_members: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    keepalive_vrf: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    keepalive_ip_peer1: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    keepalive_ip_peer2: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
