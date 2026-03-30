"""Route Control DB models — all entries stored as JSONB arrays (E.21).

Tables: ipv4_prefix_lists, ipv6_prefix_lists, standard_community_lists,
extended_community_lists, ip_as_path_access_lists, route_maps, ip_acls,
mac_lists, object_groups, time_ranges.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


# ═══════════════════════════════════════════════════════════════════
# IPv4 Prefix Lists
# ═══════════════════════════════════════════════════════════════════

class Ipv4PrefixListDB(UUIDTimestampMixin, Base):
    __tablename__ = "ipv4_prefix_lists"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_ipv4_pl_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# IPv6 Prefix Lists
# ═══════════════════════════════════════════════════════════════════

class Ipv6PrefixListDB(UUIDTimestampMixin, Base):
    __tablename__ = "ipv6_prefix_lists"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_ipv6_pl_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# Standard Community Lists
# ═══════════════════════════════════════════════════════════════════

class StandardCommunityListDB(UUIDTimestampMixin, Base):
    __tablename__ = "standard_community_lists"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_std_cl_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# Extended Community Lists
# ═══════════════════════════════════════════════════════════════════

class ExtendedCommunityListDB(UUIDTimestampMixin, Base):
    __tablename__ = "extended_community_lists"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_ext_cl_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# IP AS-Path Access Lists
# ═══════════════════════════════════════════════════════════════════

class IpAsPathAccessListDB(UUIDTimestampMixin, Base):
    __tablename__ = "ip_as_path_access_lists"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_aspath_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# Route Maps
# ═══════════════════════════════════════════════════════════════════

class RouteMapDB(UUIDTimestampMixin, Base):
    __tablename__ = "route_maps"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_route_map_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# IP ACLs
# ═══════════════════════════════════════════════════════════════════

class IpAclDB(UUIDTimestampMixin, Base):
    __tablename__ = "ip_acls"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_ip_acl_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# MAC Lists
# ═══════════════════════════════════════════════════════════════════

class MacListDB(UUIDTimestampMixin, Base):
    __tablename__ = "mac_lists"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_mac_list_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# Object Groups
# ═══════════════════════════════════════════════════════════════════

class ObjectGroupDB(UUIDTimestampMixin, Base):
    __tablename__ = "object_groups"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_obj_grp_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)


# ═══════════════════════════════════════════════════════════════════
# Time Ranges
# ═══════════════════════════════════════════════════════════════════

class TimeRangeDB(UUIDTimestampMixin, Base):
    __tablename__ = "time_ranges"
    __table_args__ = (
        UniqueConstraint("fabric_id", "name", name="uq_time_range_fabric_name"),
    )

    fabric_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("fabrics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    entries: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
