"""Pydantic request / response models -- re-exports from common."""

from app.models.common import (
    PaginatedResponse,
    TimestampMixin,
    validate_bgp_asn,
    validate_cidr,
    validate_cidr_v4,
    validate_ipv4,
    validate_ipv4_cidr,
    validate_ipv6_cidr,
    validate_mac,
    validate_multicast_v4,
    validate_vlan_id,
    validate_vni,
)

__all__ = [
    "PaginatedResponse",
    "TimestampMixin",
    "validate_bgp_asn",
    "validate_cidr",
    "validate_cidr_v4",
    "validate_ipv4",
    "validate_ipv4_cidr",
    "validate_ipv6_cidr",
    "validate_mac",
    "validate_multicast_v4",
    "validate_vlan_id",
    "validate_vni",
]
