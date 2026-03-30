"""Topology Pydantic models: vPC Peer, Fabric Link, Edge Connection, ToR Peer."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.common import TimestampMixin, validate_ipv4


# ── vPC Peer (E.6) ──────────────────────────────────────────────

class VpcPeerCreate(BaseModel):
    """Request body to create a vPC peer pair."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    peer1: str = Field(
        ...,
        max_length=128,
        description="First switch hostname.",
        example="LEAF-1"
    )
    peer2: str = Field(
        ...,
        max_length=128,
        description="Second switch hostname.",
        example="LEAF-2"
    )
    domain_id: int = Field(
        ...,
        ge=1,
        le=1000,
        description="vPC domain ID.",
        example=10
    )
    peer_link_po_id: Optional[int] = Field(
        default=None,
        description="Peer-link port-channel ID.",
        example=500
    )
    peer_link_members: Optional[list[str]] = Field(
        default=None,
        description="Peer-link member interfaces.",
        example=["Ethernet1/53", "Ethernet1/54"]
    )
    keepalive_vrf: Optional[str] = Field(
        default=None,
        description="VRF for vPC keepalive.",
        example="management"
    )
    keepalive_ip_peer1: Optional[str] = Field(
        default=None,
        description="Peer1 keepalive IPv4.",
        example="192.168.1.1"
    )
    keepalive_ip_peer2: Optional[str] = Field(
        default=None,
        description="Peer2 keepalive IPv4.",
        example="192.168.1.2"
    )

    @model_validator(mode="after")
    def _peers_differ(self) -> "VpcPeerCreate":
        if self.peer1 == self.peer2:
            raise ValueError("peer1 and peer2 must be different switches")
        return self

    @field_validator("keepalive_ip_peer1", "keepalive_ip_peer2")
    @classmethod
    def _validate_ipv4(cls, v: str | None) -> str | None:
        return validate_ipv4(v) if v else v

    @field_validator("peer_link_members")
    @classmethod
    def _validate_intf_list(cls, v: list[str] | None) -> list[str] | None:
        if v:
            import re
            pat = re.compile(r"^(?i)(?:Ethernet|Eth)\d+(?:/\d+){1,2}$")
            for intf in v:
                if not pat.match(intf):
                    raise ValueError(f"'{intf}' is not a valid physical interface")
        return v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "peer1": "LEAF-1",
                    "peer2": "LEAF-2",
                    "domain_id": 10,
                    "peer_link_po_id": 500,
                    "peer_link_members": ["Ethernet1/53", "Ethernet1/54"],
                    "keepalive_vrf": "management",
                    "keepalive_ip_peer1": "192.168.1.1",
                    "keepalive_ip_peer2": "192.168.1.2"
                }
            ]
        }
    }


class VpcPeerUpdate(BaseModel):
    """Update a vPC peer pair. Peers cannot change."""

    domain_id: Optional[int] = Field(
        default=None,
        ge=1,
        le=1000,
        description="Domain ID.",
        example=20
    )
    peer_link_po_id: Optional[int] = Field(
        default=None,
        description="Peer-link PO ID.",
        example=501
    )
    peer_link_members: Optional[list[str]] = Field(
        default=None,
        description="Peer-link members.",
        example=["Ethernet1/51", "Ethernet1/52"]
    )
    keepalive_vrf: Optional[str] = Field(
        default=None,
        description="Keepalive VRF.",
        example="default"
    )
    keepalive_ip_peer1: Optional[str] = Field(
        default=None,
        description="Peer1 keepalive IP.",
        example="10.0.0.1"
    )
    keepalive_ip_peer2: Optional[str] = Field(
        default=None,
        description="Peer2 keepalive IP.",
        example="10.0.0.2"
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "domain_id": 20,
                    "peer_link_po_id": 501,
                    "peer_link_members": ["Ethernet1/51", "Ethernet1/52"]
                }
            ]
        }
    }


class VpcPeerRead(TimestampMixin):
    """Response body for a vPC peer pair."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    peer1: str = Field(
        description="First switch hostname.",
        example="LEAF-1"
    )
    peer2: str = Field(
        description="Second switch hostname.",
        example="LEAF-2"
    )
    domain_id: int = Field(
        description="vPC domain ID.",
        example=10
    )
    peer_link_po_id: Optional[int] = Field(
        default=None,
        description="Peer-link PO ID.",
        example=500
    )
    peer_link_members: Optional[list[str]] = Field(
        default=None,
        description="Peer-link members.",
        example=["Ethernet1/53", "Ethernet1/54"]
    )
    keepalive_vrf: Optional[str] = Field(
        default=None,
        description="Keepalive VRF.",
        example="management"
    )
    keepalive_ip_peer1: Optional[str] = Field(
        default=None,
        description="Peer1 keepalive IP.",
        example="192.168.1.1"
    )
    keepalive_ip_peer2: Optional[str] = Field(
        default=None,
        description="Peer2 keepalive IP.",
        example="192.168.1.2"
    )

    model_config = {"from_attributes": True}


# ── Fabric Link (E.7) ───────────────────────────────────────────

class FabricLinkCreate(BaseModel):
    """Request body to create a fabric link."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    source_switch: str = Field(
        ...,
        max_length=128,
        description="Source switch hostname.",
        example="SPINE-1"
    )
    source_interface: str = Field(
        ...,
        description="Source interface name.",
        example="Ethernet1/1"
    )
    dest_switch: str = Field(
        ...,
        max_length=128,
        description="Destination switch hostname.",
        example="LEAF-1"
    )
    dest_interface: str = Field(
        ...,
        description="Destination interface name.",
        example="Ethernet1/49"
    )
    link_template: Optional[str] = Field(
        default=None,
        description="NDFC link template name.",
        example="spine_leaf_link"
    )
    mtu: Optional[int] = Field(
        default=None,
        ge=1500,
        le=9216,
        description="Link MTU.",
        example=9216
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI config.",
        example="description Link to LEAF-1"
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "source_switch": "SPINE-1",
                    "source_interface": "Ethernet1/1",
                    "dest_switch": "LEAF-1",
                    "dest_interface": "Ethernet1/49",
                    "link_template": "spine_leaf_link",
                    "mtu": 9216
                }
            ]
        }
    }


class FabricLinkUpdate(BaseModel):
    """Update a fabric link."""

    link_template: Optional[str] = Field(
        default=None,
        description="Link template.",
        example="spine_leaf_link_v2"
    )
    mtu: Optional[int] = Field(
        default=None,
        ge=1500,
        le=9216,
        description="Link MTU.",
        example=9000
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI.",
        example="description Updated link"
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mtu": 9000,
                    "freeform_config": "description Link to LEAF-1"
                }
            ]
        }
    }


class FabricLinkRead(TimestampMixin):
    """Response body for a fabric link."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    source_switch: str = Field(
        description="Source switch hostname.",
        example="SPINE-1"
    )
    source_interface: str = Field(
        description="Source interface.",
        example="Ethernet1/1"
    )
    dest_switch: str = Field(
        description="Destination switch hostname.",
        example="LEAF-1"
    )
    dest_interface: str = Field(
        description="Destination interface.",
        example="Ethernet1/49"
    )
    link_template: Optional[str] = Field(
        default=None,
        description="Link template.",
        example="spine_leaf_link"
    )
    mtu: Optional[int] = Field(
        default=None,
        description="Link MTU.",
        example=9216
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI.",
        example="description Link to LEAF-1"
    )

    model_config = {"from_attributes": True}


# ── Edge Connection (E.8) ───────────────────────────────────────

class EdgeConnectionCreate(BaseModel):
    """Request body to create an edge connection."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    switch_name: str = Field(
        ...,
        max_length=128,
        description="Switch hostname.",
        example="BORDER-1"
    )
    interface: str = Field(
        ...,
        description="Interface name.",
        example="Ethernet1/48"
    )
    connected_to: Optional[str] = Field(
        default=None,
        description="Connected device name.",
        example="EXTERNAL-ROUTER"
    )
    peer_ip: Optional[str] = Field(
        default=None,
        description="Peer IPv4 address.",
        example="10.99.0.2"
    )
    bgp_peer_asn: Optional[str] = Field(
        default=None,
        description="BGP peer ASN.",
        example="65100"
    )
    vrf: Optional[str] = Field(
        default=None,
        description="VRF name.",
        example="EXTERNAL-VRF"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=256,
        description="Description.",
        example="Connection to Core"
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI config.",
        example="no shutdown"
    )

    @field_validator("peer_ip")
    @classmethod
    def _validate_ip(cls, v: str | None) -> str | None:
        return validate_ipv4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "switch_name": "BORDER-1",
                    "interface": "Ethernet1/48",
                    "connected_to": "EXTERNAL-ROUTER",
                    "peer_ip": "10.99.0.2",
                    "bgp_peer_asn": "65100",
                    "vrf": "EXTERNAL-VRF"
                }
            ]
        }
    }


class EdgeConnectionUpdate(BaseModel):
    """Update an edge connection."""

    connected_to: Optional[str] = Field(
        default=None,
        description="Connected device.",
        example="CORE-ROUTER"
    )
    peer_ip: Optional[str] = Field(
        default=None,
        description="Peer IP.",
        example="10.99.0.3"
    )
    bgp_peer_asn: Optional[str] = Field(
        default=None,
        description="BGP peer ASN.",
        example="65200"
    )
    vrf: Optional[str] = Field(
        default=None,
        description="VRF.",
        example="CORE-VRF"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=256,
        description="Description.",
        example="Updated connection"
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI.",
        example="description link-to-core"
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "connected_to": "CORE-ROUTER",
                    "peer_ip": "10.99.0.3"
                }
            ]
        }
    }


class EdgeConnectionRead(TimestampMixin):
    """Response body for an edge connection."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    switch_name: str = Field(
        description="Switch hostname.",
        example="BORDER-1"
    )
    interface: str = Field(
        description="Interface name.",
        example="Ethernet1/48"
    )
    connected_to: Optional[str] = Field(
        default=None,
        description="Connected device.",
        example="EXTERNAL-ROUTER"
    )
    peer_ip: Optional[str] = Field(
        default=None,
        description="Peer IP.",
        example="10.99.0.2"
    )
    bgp_peer_asn: Optional[str] = Field(
        default=None,
        description="BGP peer ASN.",
        example="65100"
    )
    vrf: Optional[str] = Field(
        default=None,
        description="VRF.",
        example="EXTERNAL-VRF"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description.",
        example="Connection to Core"
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI.",
        example="no shutdown"
    )

    model_config = {"from_attributes": True}


# ── ToR Peer (E.9) ──────────────────────────────────────────────

class ToRPeerCreate(BaseModel):
    """Request body to create a ToR peer pair."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    switch_name: str = Field(
        ...,
        max_length=128,
        description="ToR switch hostname.",
        example="TOR-1"
    )
    peer_switch: str = Field(
        ...,
        max_length=128,
        description="Peer ToR switch hostname.",
        example="TOR-2"
    )
    link_interfaces: Optional[list[str]] = Field(
        default=None,
        description="Link interfaces.",
        example=["Ethernet1/47", "Ethernet1/48"]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "switch_name": "TOR-1",
                    "peer_switch": "TOR-2",
                    "link_interfaces": ["Ethernet1/47", "Ethernet1/48"],
                }
            ]
        }
    }


class ToRPeerUpdate(BaseModel):
    """Update a ToR peer pair."""

    link_interfaces: Optional[list[str]] = Field(
        default=None,
        description="Link interfaces.",
        example=["Ethernet1/45", "Ethernet1/46"]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "link_interfaces": ["Ethernet1/45", "Ethernet1/46"]
                }
            ]
        }
    }


class ToRPeerRead(TimestampMixin):
    """Response body for a ToR peer pair."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    switch_name: str = Field(
        description="ToR switch hostname.",
        example="TOR-1"
    )
    peer_switch: str = Field(
        description="Peer ToR hostname.",
        example="TOR-2"
    )
    link_interfaces: Optional[list[str]] = Field(
        default=None,
        description="Link interfaces.",
        example=["Ethernet1/47", "Ethernet1/48"]
    )

    model_config = {"from_attributes": True}
