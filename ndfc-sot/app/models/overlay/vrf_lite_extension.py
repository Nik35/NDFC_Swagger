"""VRF Lite Extension Pydantic models (E.20)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.common import TimestampMixin, validate_bgp_asn, validate_ipv4, validate_ipv6


class VrfLiteExtensionCreate(BaseModel):
    """Request body to create a VRF Lite extension."""

    fabric_id: UUID = Field(..., description="Parent fabric UUID.")
    vrf_name: str = Field(..., max_length=32, description="VRF name.")
    switch_name: str = Field(..., max_length=128, description="Switch hostname.")
    interface: str = Field(..., description="Interface name (e.g. Ethernet1/48).")
    ipv4_neighbor: Optional[str] = Field(default=None, description="IPv4 neighbor address.")
    ipv6_neighbor: Optional[str] = Field(default=None, description="IPv6 neighbor address.")
    peer_vrf: Optional[str] = Field(default=None, description="Peer VRF name.")
    dot1q_vlan: Optional[int] = Field(default=None, ge=1, le=4094, description="802.1Q VLAN ID.")
    bgp_peer_asn: Optional[str] = Field(default=None, description="BGP peer ASN.")
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI config.")

    @field_validator("ipv4_neighbor")
    @classmethod
    def _v4(cls, v: str | None) -> str | None:
        return validate_ipv4(v) if v else v

    @field_validator("ipv6_neighbor")
    @classmethod
    def _v6(cls, v: str | None) -> str | None:
        return validate_ipv6(v) if v else v

    @field_validator("bgp_peer_asn")
    @classmethod
    def _asn(cls, v: str | None) -> str | None:
        return validate_bgp_asn(v) if v else v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "00000000-0000-0000-0000-000000000001",
                    "vrf_name": "VRF_PROD",
                    "switch_name": "BORDER-1",
                    "interface": "Ethernet1/48",
                    "ipv4_neighbor": "10.99.0.2",
                    "bgp_peer_asn": "65100",
                }
            ]
        }
    }


class VrfLiteExtensionUpdate(BaseModel):
    """Update a VRF Lite extension."""

    ipv4_neighbor: Optional[str] = Field(default=None, description="IPv4 neighbor.")
    ipv6_neighbor: Optional[str] = Field(default=None, description="IPv6 neighbor.")
    peer_vrf: Optional[str] = Field(default=None, description="Peer VRF.")
    dot1q_vlan: Optional[int] = Field(default=None, ge=1, le=4094, description="802.1Q VLAN.")
    bgp_peer_asn: Optional[str] = Field(default=None, description="BGP peer ASN.")
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI.")


class VrfLiteExtensionRead(TimestampMixin):
    """Response body for a VRF Lite extension."""

    fabric_id: UUID = Field(description="Parent fabric UUID.")
    vrf_name: str = Field(description="VRF name.")
    switch_name: str = Field(description="Switch hostname.")
    interface: str = Field(description="Interface name.")
    ipv4_neighbor: Optional[str] = Field(default=None, description="IPv4 neighbor.")
    ipv6_neighbor: Optional[str] = Field(default=None, description="IPv6 neighbor.")
    peer_vrf: Optional[str] = Field(default=None, description="Peer VRF.")
    dot1q_vlan: Optional[int] = Field(default=None, description="802.1Q VLAN.")
    bgp_peer_asn: Optional[str] = Field(default=None, description="BGP peer ASN.")
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI.")

    model_config = {"from_attributes": True}
