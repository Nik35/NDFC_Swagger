"""SQLAlchemy models for topology tables: fabric_links, edge_connections, tor_peers (E.7-E.9)."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class FabricLinkDB(UUIDTimestampMixin, Base):
    """E.7 Fabric Link."""

    __tablename__ = "fabric_links"
    __table_args__ = (
        UniqueConstraint(
            "fabric_id", "source_switch", "source_interface",
            name="uq_fabric_link_src",
        ),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_switch: Mapped[str] = mapped_column(String(64), nullable=False)
    source_interface: Mapped[str] = mapped_column(String(64), nullable=False)
    dest_switch: Mapped[str] = mapped_column(String(64), nullable=False)
    dest_interface: Mapped[str] = mapped_column(String(64), nullable=False)
    link_template: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    mtu: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class EdgeConnectionDB(UUIDTimestampMixin, Base):
    """E.8 Edge Connection."""

    __tablename__ = "edge_connections"
    __table_args__ = (
        UniqueConstraint(
            "fabric_id", "switch_name", "interface",
            name="uq_edge_conn_switch_intf",
        ),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    switch_name: Mapped[str] = mapped_column(String(64), nullable=False)
    interface: Mapped[str] = mapped_column(String(64), nullable=False)
    connected_to: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    peer_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    bgp_peer_asn: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    vrf: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    freeform_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class TorPeerDB(UUIDTimestampMixin, Base):
    """E.9 ToR Peer."""

    __tablename__ = "tor_peers"
    __table_args__ = (
        UniqueConstraint(
            "fabric_id", "switch_name", "peer_switch",
            name="uq_tor_peer_pair",
        ),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    switch_name: Mapped[str] = mapped_column(String(64), nullable=False)
    peer_switch: Mapped[str] = mapped_column(String(64), nullable=False)
    link_interfaces: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
