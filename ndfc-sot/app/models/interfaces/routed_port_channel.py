"""Routed port-channel Pydantic model."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field, field_validator

from app.models.common import validate_cidr
from app.models.interfaces.base import InterfaceBase, validate_mtu


class RoutedPortChannelCreate(InterfaceBase):
    """Create a routed port-channel."""

    mode: Literal["routed_port_channel"] = Field(..., description="Interface mode discriminator.", example="routed_port_channel")
    name: str = Field(..., pattern=r"^[Pp]ort-channel\d+$", description="Port-channel name (e.g. Port-channel50).", example="Port-channel50")
    vrf: Optional[str] = Field(default=None, description="VRF name.", example="PROD")
    ipv4_address: Optional[str] = Field(default=None, description="IPv4 CIDR.", example="10.10.50.1/30")
    ipv6_address: Optional[str] = Field(default=None, description="IPv6 CIDR.", example="2001:db8:50::1/126")
    mtu: Optional[str] = Field(default=None, description="MTU.", example="9216")
    pc_mode: Optional[Literal["active", "passive", "on"]] = Field(default="active", description="LACP mode.", example="active")
    members: Optional[list[str]] = Field(default=None, description="Member interfaces.", example=["Ethernet1/49", "Ethernet1/50"])

    _validate_mtu = field_validator("mtu")(validate_mtu)

    @field_validator("ipv4_address", "ipv6_address")
    @classmethod
    def _cidr(cls, v: str | None) -> str | None:
        return validate_cidr(v) if v else v

    @field_validator("members")
    @classmethod
    def _validate_members(cls, v: list[str] | None) -> list[str] | None:
        if v:
            import re
            pat = re.compile(r"^(?i)(?:Ethernet|Eth)\d+(?:/\d+){1,2}$")
            for m in v:
                if not pat.match(m):
                    raise ValueError(f"Member '{m}' is not a valid physical interface")
        return v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "routed_port_channel",
                    "name": "Port-channel50",
                    "description": "L3 Port-channel to Core",
                    "enabled": True,
                    "vrf": "PROD",
                    "ipv4_address": "10.10.50.1/30",
                    "ipv6_address": "2001:db8:50::1/126",
                    "mtu": "9216",
                    "pc_mode": "active",
                    "members": ["Ethernet1/49", "Ethernet1/50"]
                }
            ]
        }
    }