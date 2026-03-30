"""SQLAlchemy models for all 8 underlay tables (E.10–E.17).

Each is a 1:1 singleton per fabric.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


# ═══════════════════════════════════════════════════════════════════
# E.10 Underlay General
# ═══════════════════════════════════════════════════════════════════

class UnderlayGeneralDB(UUIDTimestampMixin, Base):
    __tablename__ = "underlay_general"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_underlay_general_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    replication_mode: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, default="multicast"
    )
    enable_trm: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    underlay_routing_protocol: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, default="ospf"
    )
    link_state_routing_tag: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, default="UNDERLAY"
    )
    enable_pvlan: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    enable_netflow: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    stp_root_bridge_option: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, default="unmanaged"
    )
    brownfield_import: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )


# ═══════════════════════════════════════════════════════════════════
# E.11 Underlay IPv4
# ═══════════════════════════════════════════════════════════════════

class UnderlayIpv4DB(UUIDTimestampMixin, Base):
    __tablename__ = "underlay_ipv4"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_underlay_ipv4_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    underlay_routing_loopback_ip_range: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    underlay_vtep_loopback_ip_range: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    underlay_rp_loopback_ip_range: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )
    subnet_range: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    underlay_subnet_mask: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=30
    )


# ═══════════════════════════════════════════════════════════════════
# E.12 Underlay IPv6
# ═══════════════════════════════════════════════════════════════════

class UnderlayIpv6DB(UUIDTimestampMixin, Base):
    __tablename__ = "underlay_ipv6"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_underlay_ipv6_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    enable_ipv6_underlay: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    ipv6_link_local_range: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    underlay_v6_routing_loopback_range: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    underlay_v6_vtep_loopback_range: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )


# ═══════════════════════════════════════════════════════════════════
# E.13 Underlay IS-IS
# ═══════════════════════════════════════════════════════════════════

class UnderlayIsisDB(UUIDTimestampMixin, Base):
    __tablename__ = "underlay_isis"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_underlay_isis_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    authentication_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    authentication_key: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    authentication_key_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    overload_bit: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    level: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, default="level-2"
    )
    network_type: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, default="p2p"
    )


# ═══════════════════════════════════════════════════════════════════
# E.14 Underlay OSPF
# ═══════════════════════════════════════════════════════════════════

class UnderlayOspfDB(UUIDTimestampMixin, Base):
    __tablename__ = "underlay_ospf"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_underlay_ospf_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    area_id: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, default="0.0.0.0"
    )
    authentication_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    authentication_key: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    authentication_key_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )


# ═══════════════════════════════════════════════════════════════════
# E.15 Underlay BGP
# ═══════════════════════════════════════════════════════════════════

class UnderlayBgpDB(UUIDTimestampMixin, Base):
    __tablename__ = "underlay_bgp"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_underlay_bgp_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    authentication_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    authentication_key_type: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=3
    )
    authentication_key: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )


# ═══════════════════════════════════════════════════════════════════
# E.16 Underlay BFD
# ═══════════════════════════════════════════════════════════════════

class UnderlayBfdDB(UUIDTimestampMixin, Base):
    __tablename__ = "underlay_bfd"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_underlay_bfd_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    min_tx: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=50
    )
    min_rx: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=50
    )
    multiplier: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=3
    )
    enable_ibgp: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    enable_ospf: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    enable_isis: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    enable_pim: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )


# ═══════════════════════════════════════════════════════════════════
# E.17 Underlay Multicast
# ═══════════════════════════════════════════════════════════════════

class UnderlayMulticastDB(UUIDTimestampMixin, Base):
    __tablename__ = "underlay_multicast"
    __table_args__ = (
        UniqueConstraint("fabric_id", name="uq_underlay_multicast_fabric"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    group_subnet: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True, default="239.1.1.0/25"
    )
    rendezvous_points: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=2
    )
    rp_mode: Mapped[Optional[str]] = mapped_column(
        String(8), nullable=True, default="asm"
    )
    underlay_rp_loopback_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=254
    )
    trm_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
    trm_bgw_msite_enable: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, default=False
    )
