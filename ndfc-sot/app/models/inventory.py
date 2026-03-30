"""Switch / inventory Pydantic models."""

from __future__ import annotations

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.common import TimestampMixin, validate_ipv4, validate_ipv6


class SwitchRole(str, Enum):
    SPINE = "spine"
    LEAF = "leaf"
    BORDER = "border"
    BORDER_SPINE = "border_spine"
    BORDER_GATEWAY = "border_gateway"
    BORDER_GATEWAY_SPINE = "border_gateway_spine"
    SUPER_SPINE = "super_spine"
    BORDER_SUPER_SPINE = "border_super_spine"
    ACCESS = "access"


class SwitchCreate(BaseModel):
    """Request body to create / register a switch."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Switch hostname.",
        examples=["LEAF-1"]
    )
    serial_number: Optional[str] = Field(
        default=None,
        max_length=16,
        pattern=r"^[a-zA-Z0-9_.:-]{1,16}$",
        description="Chassis serial number.",
        examples=["SAL12345678"]
    )
    role: SwitchRole = Field(
        default=SwitchRole.LEAF,
        description="Fabric role.",
        examples=["leaf"]
    )
    routing_loopback_id: Optional[int] = Field(
        default=0,
        ge=0,
        le=1023,
        description="Routing loopback interface ID.",
        examples=[0]
    )
    vtep_loopback_id: Optional[int] = Field(
        default=1,
        ge=0,
        le=1023,
        description="VTEP loopback interface ID.",
        examples=[1]
    )
    routing_loopback_ipv4: Optional[str] = Field(
        default=None,
        description="Routing loopback IPv4 address.",
        examples=["10.250.0.1"]
    )
    routing_loopback_ipv6: Optional[str] = Field(
        default=None,
        description="Routing loopback IPv6 address.",
        examples=["2001:db8:0:1::1"]
    )
    vtep_loopback_ipv4: Optional[str] = Field(
        default=None,
        description="VTEP loopback IPv4 address.",
        examples=["10.251.0.1"]
    )
    mgmt_ip: Optional[str] = Field(
        default=None,
        description="Management IPv4 address.",
        examples=["192.168.1.10"]
    )
    mgmt_gw: Optional[str] = Field(
        default=None,
        description="Management default gateway IPv4.",
        examples=["192.168.1.1"]
    )
    seed_ip: Optional[str] = Field(
        default=None,
        description="Seed/discovery IPv4 address.",
        examples=["10.1.1.50"]
    )
    max_paths: Optional[int] = Field(
        default=None,
        ge=1,
        le=64,
        description="Maximum ECMP paths.",
        examples=[16]
    )
    system_nve_id: Optional[int] = Field(
        default=1,
        ge=1,
        le=4,
        description="System NVE interface ID.",
        examples=[1]
    )
    data_link: Optional[str] = Field(
        default=None,
        description="Data link description.",
        examples=["Link to Core-1"]
    )
    vpc_domain_id: Optional[int] = Field(
        default=None,
        description="vPC domain ID.",
        examples=[10]
    )
    vpc_peer_link: Optional[str] = Field(
        default=None,
        description="vPC peer-link interface.",
        examples=["Port-channel500"]
    )
    vpc_peer_ip: Optional[str] = Field(
        default=None,
        description="vPC peer keepalive IP.",
        examples=["1.1.1.1"]
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform NX-OS CLI config.",
        examples=["feature bgp"]
    )

    @field_validator("routing_loopback_ipv4", "vtep_loopback_ipv4", "mgmt_ip", "mgmt_gw", "seed_ip", "vpc_peer_ip")
    @classmethod
    def _v4(cls, v: str | None) -> str | None:
        return validate_ipv4(v) if v else v

    @field_validator("routing_loopback_ipv6")
    @classmethod
    def _v6(cls, v: str | None) -> str | None:
        return validate_ipv6(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "LEAF-1",
                    "serial_number": "SAL12345678",
                    "role": "leaf",
                    "routing_loopback_id": 0,
                    "vtep_loopback_id": 1,
                    "routing_loopback_ipv4": "10.250.0.1",
                    "vtep_loopback_ipv4": "10.251.0.1",
                    "mgmt_ip": "192.168.1.10",
                    "mgmt_gw": "192.168.1.1",
                }
            ]
        }
    }


class SwitchUpdate(BaseModel):
    """Partial update for a switch."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=128,
        description="Hostname.",
        examples=["LEAF-1-NEW"]
    )
    serial_number: Optional[str] = Field(
        default=None,
        max_length=16,
        description="Serial number.",
        examples=["SAL87654321"]
    )
    role: Optional[SwitchRole] = Field(
        default=None,
        description="Fabric role.",
        examples=["border"]
    )
    routing_loopback_id: Optional[int] = Field(
        default=None,
        ge=0,
        le=1023,
        description="Routing loopback ID.",
        examples=[100]
    )
    vtep_loopback_id: Optional[int] = Field(
        default=None,
        ge=0,
        le=1023,
        description="VTEP loopback ID.",
        examples=[101]
    )
    routing_loopback_ipv4: Optional[str] = Field(
        default=None,
        description="Routing loopback IPv4.",
        examples=["10.250.0.2"]
    )
    routing_loopback_ipv6: Optional[str] = Field(
        default=None,
        description="Routing loopback IPv6.",
        examples=["2001:db8:0:1::2"]
    )
    vtep_loopback_ipv4: Optional[str] = Field(
        default=None,
        description="VTEP loopback IPv4.",
        examples=["10.251.0.2"]
    )
    mgmt_ip: Optional[str] = Field(
        default=None,
        description="Management IPv4.",
        examples=["192.168.1.11"]
    )
    mgmt_gw: Optional[str] = Field(
        default=None,
        description="Management gateway.",
        examples=["192.168.1.1"]
    )
    seed_ip: Optional[str] = Field(
        default=None,
        description="Seed IP.",
        examples=["10.1.1.51"]
    )
    max_paths: Optional[int] = Field(
        default=None,
        ge=1,
        le=64,
        description="Max ECMP paths.",
        examples=[32]
    )
    system_nve_id: Optional[int] = Field(
        default=None,
        ge=1,
        le=4,
        description="NVE ID.",
        examples=[2]
    )
    data_link: Optional[str] = Field(
        default=None,
        description="Data link.",
        examples=["Backup link"]
    )
    vpc_domain_id: Optional[int] = Field(
        default=None,
        description="vPC domain ID.",
        examples=[20]
    )
    vpc_peer_link: Optional[str] = Field(
        default=None,
        description="vPC peer-link.",
        examples=["Port-channel600"]
    )
    vpc_peer_ip: Optional[str] = Field(
        default=None,
        description="vPC peer IP.",
        examples=["2.2.2.2"]
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI.",
        examples=["feature interface-vlan"]
    )

    @field_validator("routing_loopback_ipv4", "vtep_loopback_ipv4", "mgmt_ip", "mgmt_gw", "seed_ip", "vpc_peer_ip")
    @classmethod
    def _v4(cls, v: str | None) -> str | None:
        return validate_ipv4(v) if v else v

    @field_validator("routing_loopback_ipv6")
    @classmethod
    def _v6(cls, v: str | None) -> str | None:
        return validate_ipv6(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "LEAF-1-NEW",
                    "role": "border"
                }
            ]
        }
    }


class SwitchRead(TimestampMixin):
    """Response body for a switch."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        description="Switch hostname.",
        examples=["LEAF-1"]
    )
    serial_number: Optional[str] = Field(
        default=None,
        description="Serial number.",
        examples=["SAL12345678"]
    )
    role: SwitchRole = Field(
        description="Fabric role.",
        examples=["leaf"]
    )
    routing_loopback_id: Optional[int] = Field(
        default=None,
        description="Routing loopback ID.",
        examples=[0]
    )
    vtep_loopback_id: Optional[int] = Field(
        default=None,
        description="VTEP loopback ID.",
        examples=[1]
    )
    routing_loopback_ipv4: Optional[str] = Field(
        default=None,
        description="Routing loopback IPv4.",
        examples=["10.250.0.1"]
    )
    routing_loopback_ipv6: Optional[str] = Field(
        default=None,
        description="Routing loopback IPv6.",
        examples=["2001:db8:0:1::1"]
    )
    vtep_loopback_ipv4: Optional[str] = Field(
        default=None,
        description="VTEP loopback IPv4.",
        examples=["10.251.0.1"]
    )
    mgmt_ip: Optional[str] = Field(
        default=None,
        description="Management IPv4.",
        examples=["192.168.1.10"]
    )
    mgmt_gw: Optional[str] = Field(
        default=None,
        description="Management gateway.",
        examples=["192.168.1.1"]
    )
    seed_ip: Optional[str] = Field(
        default=None,
        description="Seed IP.",
        examples=["10.1.1.50"]
    )
    max_paths: Optional[int] = Field(
        default=None,
        description="Max ECMP paths.",
        examples=[16]
    )
    system_nve_id: Optional[int] = Field(
        default=None,
        description="NVE ID.",
        examples=[1]
    )
    data_link: Optional[str] = Field(
        default=None,
        description="Data link.",
        examples=["Link to Core-1"]
    )
    vpc_domain_id: Optional[int] = Field(
        default=None,
        description="vPC domain ID.",
        examples=[10]
    )
    vpc_peer_link: Optional[str] = Field(
        default=None,
        description="vPC peer-link.",
        examples=["Port-channel500"]
    )
    vpc_peer_ip: Optional[str] = Field(
        default=None,
        description="vPC peer IP.",
        examples=["1.1.1.1"]
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI.",
        examples=["feature bgp"]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
