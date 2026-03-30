"""SQLAlchemy models for Network and Network switch attachments (E.19)."""

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


class NetworkDB(UUIDTimestampMixin, Base):
    __tablename__ = "networks"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_network_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    network_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vlan_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vlan_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    vrf_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    gateway_ipv4: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    gateway_ipv6: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    suppress_arp: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    enable_ir: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    mtu: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=9216
    )
    routing_tag: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=12345
    )
    is_l2_only: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    multicast_group: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    dhcp_server_addr_1: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    dhcp_server_addr_2: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    dhcp_server_addr_3: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    dhcp_server_vrf: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    loopback_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    enable_trm: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    route_map_in: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    netflow_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class NetworkSwitchAttachmentDB(UUIDTimestampMixin, Base):
    __tablename__ = "network_switch_attachments"
    __table_args__ = (
        UniqueConstraint(
            "network_id", "hostname", name="uq_net_attach_net_switch"
        ),
    )

    network_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("networks.id", ondelete="CASCADE"),
        nullable=False,
    )
    hostname: Mapped[str] = mapped_column(String(64), nullable=False)
    ports: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
