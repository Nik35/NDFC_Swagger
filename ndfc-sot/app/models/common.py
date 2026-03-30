"""Shared Pydantic helpers and validators."""

from __future__ import annotations

import ipaddress
import re
from datetime import datetime
from typing import Generic, TypeVar, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

T = TypeVar("T")


class TimestampMixin(BaseModel):
    """Adds id + created_at / updated_at to read models."""

    id: UUID
    created_at: datetime
    updated_at: datetime


def validate_ipv4(v: str) -> str:
    """Validate an IPv4 address string."""
    try:
        ipaddress.IPv4Address(v)
    except (ipaddress.AddressValueError, ValueError) as exc:
        raise ValueError(f"Invalid IPv4 address: {v}") from exc
    return v


def validate_ipv6(v: str) -> str:
    """Validate an IPv6 address string."""
    try:
        ipaddress.IPv6Address(v)
    except (ipaddress.AddressValueError, ValueError) as exc:
        raise ValueError(f"Invalid IPv6 address: {v}") from exc
    return v


def validate_cidr(v: str) -> str:
    """Validate an IPv4 or IPv6 CIDR string."""
    try:
        ipaddress.ip_interface(v)
    except ValueError as exc:
        raise ValueError(f"Invalid CIDR notation: {v}") from exc
    return v


def validate_ipv4_cidr(v: str) -> str:
    """Validate an IPv4 CIDR string."""
    try:
        ipaddress.IPv4Interface(v)
    except (ipaddress.AddressValueError, ValueError) as exc:
        raise ValueError(f"Invalid IPv4 CIDR: {v}") from exc
    return v


# Alias used by underlay/ipv4 and route_control/ip_prefix_list
validate_cidr_v4 = validate_ipv4_cidr


def validate_ipv6_cidr(v: str) -> str:
    """Validate an IPv6 CIDR string."""
    try:
        ipaddress.IPv6Interface(v)
    except (ipaddress.AddressValueError, ValueError) as exc:
        raise ValueError(f"Invalid IPv6 CIDR: {v}") from exc
    return v


def validate_multicast_v4(v: str) -> str:
    """Validate an IPv4 multicast address (224.0.0.0 – 239.255.255.255)."""
    try:
        addr = ipaddress.IPv4Address(v)
    except (ipaddress.AddressValueError, ValueError) as exc:
        raise ValueError(f"Invalid IPv4 address: {v}") from exc
    if not addr.is_multicast:
        raise ValueError(f"Not a multicast address: {v}")
    return v


def validate_mac(v: str) -> str:
    """Validate and normalise a MAC address to xxxx.xxxx.xxxx format."""
    cleaned = re.sub(r"[.:\-]", "", v)
    if len(cleaned) != 12 or not re.fullmatch(r"[0-9a-fA-F]{12}", cleaned):
        raise ValueError(f"Invalid MAC address: {v}")
    lower = cleaned.lower()
    return f"{lower[0:4]}.{lower[4:8]}.{lower[8:12]}"


def validate_bgp_asn(v: str) -> str:
    """Validate a BGP ASN in plain or asdot notation."""
    # Plain integer
    if re.fullmatch(r"\d+", v):
        asn = int(v)
        if 1 <= asn <= 4294967295:
            return v
        raise ValueError(f"BGP ASN out of range: {v}")
    # asdot notation: high.low
    m = re.fullmatch(r"(\d+)\.(\d+)", v)
    if m:
        high, low = int(m.group(1)), int(m.group(2))
        if 0 <= high <= 65535 and 0 <= low <= 65535:
            return v
        raise ValueError(f"BGP ASN asdot out of range: {v}")
    raise ValueError(f"Invalid BGP ASN format: {v}")


def validate_vlan_id(v: int) -> int:
    """Validate VLAN ID (1-4094)."""
    if not 1 <= v <= 4094:
        raise ValueError(f"VLAN ID must be 1-4094, got {v}")
    return v


def validate_vni(v: int) -> int:
    """Validate VNI (1-16777214)."""
    if not 1 <= v <= 16777214:
        raise ValueError(f"VNI must be 1-16777214, got {v}")
    return v


# ---------------------------------------------------------------------------
# Paginated response wrapper
# ---------------------------------------------------------------------------

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response."""

    items: list[T]
    total: int
    page: int
    page_size: int