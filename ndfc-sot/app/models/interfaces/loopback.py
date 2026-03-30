"""Loopback interface Pydantic model."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.common import validate_cidr
from app.models.interfaces.base import InterfaceBase


class SecondaryIpv4(BaseModel):
    """Secondary IPv4 address on a loopback."""

    ipv4_address: str = Field(..., description="Secondary IPv4 in CIDR notation.", example="10.1.1.2/32")
    route_tag: Optional[int] = Field(default=None, description="Route tag.", example=100)

    @field_validator("ipv4_address")
    @classmethod
    def _validate(cls, v: str) -> str:
        return validate_cidr(v)

    model_config = {"extra": "forbid"}


class LoopbackInterfaceCreate(InterfaceBase):
    """Create a loopback interface."""

    mode: Literal["loopback", "fabric_loopback"] = Field(..., description="Interface mode discriminator.", example="loopback")
    name: str = Field(..., pattern=r"^[Ll]oopback\d+$", description="Loopback interface name (e.g. Loopback0).", example="Loopback0")
    vrf: Optional[str] = Field(default=None, description="VRF name.", example="default")
    ipv4_address: Optional[str] = Field(default=None, description="Primary IPv4 CIDR.", example="10.255.0.1/32")
    ipv6_address: Optional[str] = Field(default=None, description="Primary IPv6 CIDR.", example="2001:db8::1/128")
    ipv4_route_tag: Optional[int] = Field(default=None, description="IPv4 route tag.", example=100)
    secondary_ipv4: Optional[list[SecondaryIpv4]] = Field(default=None, description="Secondary IPv4 addresses.", example=[{"ipv4_address": "10.1.1.2/32", "route_tag": 100}])

    @field_validator("ipv4_address", "ipv6_address")
    @classmethod
    def _validate_cidr(cls, v: str | None) -> str | None:
        if v is not None:
            return validate_cidr(v)
        return v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "loopback",
                    "name": "Loopback0",
                    "ipv4_address": "10.255.0.1/32",
                    "description": "Routing loopback",
                    "enabled": True,
                    "vrf": "default",
                    "ipv4_route_tag": 100,
                    "secondary_ipv4": [
                        {"ipv4_address": "10.1.1.2/32", "route_tag": 200}
                    ]
                }
            ]
        }
    }