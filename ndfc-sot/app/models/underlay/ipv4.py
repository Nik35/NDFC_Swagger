"""Underlay IPv4 Pydantic models (E.11)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.common import TimestampMixin, validate_cidr_v4


class UnderlayIpv4Create(BaseModel):
    """Underlay IPv4 configuration (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID that this IPv4 underlay configuration belongs to.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    underlay_routing_loopback_ip_range: Optional[str] = Field(
        default="10.2.0.0/22",
        description="IPv4 address pool used for routing loopback interfaces (e.g., Loopback0) on all switches in the fabric.",
        example="10.2.0.0/22",
    )
    underlay_vtep_loopback_ip_range: Optional[str] = Field(
        default="10.3.0.0/22",
        description="IPv4 address pool used for VTEP (Virtual Tunnel End Point) loopback interfaces on leaf and border nodes.",
        example="10.3.0.0/22",
    )
    underlay_rp_loopback_ip_range: Optional[str] = Field(
        default="10.254.254.0/24",
        description="IPv4 address pool used for Rendezvous Point (RP) loopback interfaces in the multicast underlay.",
        example="10.254.254.0/24",
    )
    subnet_range: Optional[str] = Field(
        default="10.4.0.0/16",
        description="IPv4 address pool for point-to-point (P2P) links between switches (spines, leaves, and borders).",
        example="10.4.0.0/16",
    )
    underlay_subnet_mask: Optional[int] = Field(
        default=30,
        ge=1,
        le=31,
        description="Prefix length for individual point-to-point subnets carved from the 'subnet_range'. Defaults to 30.",
        example=30,
    )

    @field_validator(
        "underlay_routing_loopback_ip_range",
        "underlay_vtep_loopback_ip_range",
        "underlay_rp_loopback_ip_range",
        "subnet_range",
    )
    @classmethod
    def _validate_cidr(cls, v: str | None) -> str | None:
        return validate_cidr_v4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "underlay_routing_loopback_ip_range": "10.250.0.0/24",
                    "underlay_vtep_loopback_ip_range": "10.251.0.0/24",
                    "underlay_rp_loopback_ip_range": "10.252.0.0/24",
                    "subnet_range": "10.253.0.0/16",
                    "underlay_subnet_mask": 30,
                }
            ]
        },
    }


class UnderlayIpv4Update(BaseModel):
    """Update underlay IPv4 — all optional."""

    underlay_routing_loopback_ip_range: Optional[str] = Field(
        default=None,
        description="Updated IPv4 pool for routing loopbacks.",
        example="10.250.0.0/24",
    )
    underlay_vtep_loopback_ip_range: Optional[str] = Field(
        default=None,
        description="Updated IPv4 pool for VTEP loopbacks.",
        example="10.251.0.0/24",
    )
    underlay_rp_loopback_ip_range: Optional[str] = Field(
        default=None,
        description="Updated IPv4 pool for RP loopbacks.",
        example="10.252.0.0/24",
    )
    subnet_range: Optional[str] = Field(
        default=None,
        description="Updated IPv4 pool for P2P subnets.",
        example="10.253.0.0/24",
    )
    underlay_subnet_mask: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="Updated prefix length for P2P subnets.",
        example=30,
    )

    @field_validator(
        "underlay_routing_loopback_ip_range",
        "underlay_vtep_loopback_ip_range",
        "underlay_rp_loopback_ip_range",
        "subnet_range",
    )
    @classmethod
    def _validate_cidr(cls, v: str | None) -> str | None:
        return validate_cidr_v4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "underlay_routing_loopback_ip_range": "10.250.0.0/24",
                    "underlay_vtep_loopback_ip_range": "10.251.0.0/24",
                }
            ]
        },
    }


class UnderlayIpv4Read(TimestampMixin):
    """Response body for underlay IPv4."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    underlay_routing_loopback_ip_range: Optional[str] = Field(
        default=None,
        description="Current IPv4 pool for routing loopbacks.",
        example="10.250.0.0/24",
    )
    underlay_vtep_loopback_ip_range: Optional[str] = Field(
        default=None,
        description="Current IPv4 pool for VTEP loopbacks.",
        example="10.251.0.0/24",
    )
    underlay_rp_loopback_ip_range: Optional[str] = Field(
        default=None,
        description="Current IPv4 pool for RP loopbacks.",
        example="10.252.0.0/24",
    )
    subnet_range: Optional[str] = Field(
        default=None,
        description="Current IPv4 pool for P2P subnets.",
        example="10.253.0.0/24",
    )
    underlay_subnet_mask: Optional[int] = Field(
        default=None,
        description="Current prefix length for P2P subnets.",
        example=30,
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174001",
                    "underlay_routing_loopback_ip_range": "10.250.0.0/24",
                    "underlay_vtep_loopback_ip_range": "10.251.0.0/24",
                    "underlay_rp_loopback_ip_range": "10.252.0.0/24",
                    "subnet_range": "10.253.0.0/24",
                    "underlay_subnet_mask": 30,
                    "created_at": "2023-10-27T10:00:00Z",
                    "updated_at": "2023-10-27T10:00:00Z",
                }
            ]
        },
    }
