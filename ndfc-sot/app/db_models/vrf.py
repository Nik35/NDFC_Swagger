"""SQLAlchemy models for VRF and VRF switch attachments (E.18)."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class VrfDB(UUIDTimestampMixin, Base):
    __tablename__ = "vrfs"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_vrf_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    vrf_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vlan_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vrf_description: Mapped[Optional[str]] = mapped_column(String(254), nullable=True)
    route_target_both: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    route_target_import: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    route_target_export: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    route_target_import_evpn: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    route_target_export_evpn: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    ipv6_link_local_flag: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=True
    )
    max_bgp_paths: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=1
    )
    max_ibgp_paths: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=2
    )
    advertise_host_routes: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    advertise_default_route: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=True
    )
    enable_trm: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    rp_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    rp_external: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    underlay_mcast_ip: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    overlay_mcast_group: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    netflow_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    no_rp: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    route_map_in: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    route_map_out: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class VrfSwitchAttachmentDB(UUIDTimestampMixin, Base):
    __tablename__ = "vrf_switch_attachments"
    __table_args__ = (
        UniqueConstraint("vrf_id", "hostname", name="uq_vrf_attach_vrf_switch"),
    )

    vrf_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vrfs.id", ondelete="CASCADE"),
        nullable=False,
    )
    hostname: Mapped[str] = mapped_column(String(64), nullable=False)
    vrf_lite: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
