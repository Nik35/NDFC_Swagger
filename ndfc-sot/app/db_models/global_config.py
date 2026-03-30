"""SQLAlchemy model for the ``fabric_globals`` table (E.2)."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class FabricGlobalDB(UUIDTimestampMixin, Base):
    __tablename__ = "fabric_globals"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_fabric_global_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    global_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="vxlan_evpn_ibgp"
    )
    bgp_asn: Mapped[str] = mapped_column(String(16), nullable=False)
    route_reflectors: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=2
    )
    anycast_gateway_mac: Mapped[Optional[str]] = mapped_column(
        String(17), nullable=True
    )
    enable_nxapi_http: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    enable_nxapi_https: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=True
    )
    enable_realtime_backup: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    enable_scheduled_backup: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    inband_mgmt: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    bootstrap_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    dhcp_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    dns_server_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    dns_server_vrf: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, default="management"
    )
    ntp_server_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    ntp_server_vrf: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, default="management"
    )
    syslog_server_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    syslog_server_vrf: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, default="management"
    )
    syslog_severity: Mapped[Optional[str]] = mapped_column(
        String(8), nullable=True, default="5"
    )
    aaa_server_conf: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_conf_leaf: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_conf_spine: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    netflow_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    extra_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
