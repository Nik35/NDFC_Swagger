"""SQLAlchemy model for the ``switches`` table (E.4)."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class SwitchDB(UUIDTimestampMixin, Base):
    __tablename__ = "switches"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_switch_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, default="leaf")
    routing_loopback_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0
    )
    vtep_loopback_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=1
    )
    routing_loopback_ipv4: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    routing_loopback_ipv6: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    vtep_loopback_ipv4: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    mgmt_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    mgmt_gw: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    seed_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    max_paths: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    system_nve_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=1
    )
    data_link: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    vpc_domain_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vpc_peer_link: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    vpc_peer_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
