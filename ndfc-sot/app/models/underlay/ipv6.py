"""Underlay IPv6 Pydantic models (E.12)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class UnderlayIpv6Create(BaseModel):
    """Underlay IPv6 configuration (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID that this IPv6 underlay configuration belongs to.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    enable_ipv6_underlay: Optional[bool] = Field(
        default=False,
        description="Globally enable or disable IPv6 underlay routing within the fabric.",
        example=True,
    )
    ipv6_link_local_range: Optional[str] = Field(
        default="fe80::/10",
        description="IPv6 link-local address range used for auto-configuration on P2P links.",
        example="fe80::/10",
    )
    underlay_v6_routing_loopback_range: Optional[str] = Field(
        default=None,
        description="IPv6 address pool for routing loopback interfaces (e.g., Loopback0).",
        example="2001:db8:1::/64",
    )
    underlay_v6_vtep_loopback_range: Optional[str] = Field(
        default=None,
        description="IPv6 address pool for VTEP loopback interfaces on leaf and border nodes.",
        example="2001:db8:2::/64",
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "enable_ipv6_underlay": True,
                    "ipv6_link_local_range": "fe80::/10",
                    "underlay_v6_routing_loopback_range": "2001:db8:1::/64",
                    "underlay_v6_vtep_loopback_range": "2001:db8:2::/64",
                }
            ]
        },
    }


class UnderlayIpv6Update(BaseModel):
    """Update underlay IPv6 config."""

    enable_ipv6_underlay: Optional[bool] = Field(
        default=None,
        description="Updated status of IPv6 underlay routing.",
        example=True,
    )
    ipv6_link_local_range: Optional[str] = Field(
        default=None,
        description="Updated IPv6 link-local range.",
        example="fe80::/64",
    )
    underlay_v6_routing_loopback_range: Optional[str] = Field(
        default=None,
        description="Updated IPv6 routing loopback range.",
        example="2001:db8:100::/64",
    )
    underlay_v6_vtep_loopback_range: Optional[str] = Field(
        default=None,
        description="Updated IPv6 VTEP loopback range.",
        example="2001:db8:200::/64",
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "enable_ipv6_underlay": True,
                    "underlay_v6_routing_loopback_range": "2001:db8:100::/64",
                }
            ]
        },
    }


class UnderlayIpv6Read(TimestampMixin):
    """Response body for underlay IPv6."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    enable_ipv6_underlay: Optional[bool] = Field(
        default=None,
        description="Current status of IPv6 underlay routing.",
        example=True,
    )
    ipv6_link_local_range: Optional[str] = Field(
        default=None,
        description="Current IPv6 link-local range.",
        example="fe80::/10",
    )
    underlay_v6_routing_loopback_range: Optional[str] = Field(
        default=None,
        description="Current IPv6 routing loopback range.",
        example="2001:db8:1::/64",
    )
    underlay_v6_vtep_loopback_range: Optional[str] = Field(
        default=None,
        description="Current IPv6 VTEP loopback range.",
        example="2001:db8:2::/64",
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "enable_ipv6_underlay": True,
                    "ipv6_link_local_range": "fe80::/10",
                    "underlay_v6_routing_loopback_range": "2001:db8:1::/64",
                    "underlay_v6_vtep_loopback_range": "2001:db8:2::/64",
                    "created_at": "2023-10-27T10:00:00Z",
                    "updated_at": "2023-10-27T10:00:00Z",
                }
            ]
        },
    }
