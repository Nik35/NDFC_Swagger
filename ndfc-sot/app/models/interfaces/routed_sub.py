"""Routed sub-interface Pydantic model."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field, field_validator

from app.models.common import validate_cidr
from app.models.interfaces.base import InterfaceBase, validate_mtu


class RoutedSubInterfaceCreate(InterfaceBase):
    """Create a routed sub-interface."""

    mode: Literal["routed_sub"] = Field(..., description="Interface mode discriminator.", example="routed_sub")
    name: str = Field(
        ...,
        pattern=r"^(?i)(?:(?:Ethernet|Eth)\d+(?:/\d+){1,2}|[Pp]ort-channel\d+)\.\d+$",
        description="Sub-interface name (e.g. Ethernet1/1.100 or Port-channel10.100).",
        example="Ethernet1/48.100"
    )
    dot1q_id: int = Field(..., ge=1, le=4096, description="802.1Q encapsulation VLAN ID.", example=100)
    vrf: Optional[str] = Field(default=None, description="VRF name.", example="PROD")
    ipv4_address: Optional[str] = Field(default=None, description="IPv4 CIDR.", example="10.10.100.1/24")
    ipv6_address: Optional[str] = Field(default=None, description="IPv6 CIDR.", example="2001:db8:100::1/64")
    mtu: Optional[str] = Field(default=None, description="MTU.", example="9216")
    speed: Optional[Literal["auto", "100mb", "1gb", "10gb", "25gb", "40gb", "100gb"]] = Field(
        default=None, description="Interface speed.", example="10gb"
    )

    _validate_mtu = field_validator("mtu")(validate_mtu)

    @field_validator("ipv4_address", "ipv6_address")
    @classmethod
    def _cidr(cls, v: str | None) -> str | None:
        return validate_cidr(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "routed_sub",
                    "name": "Ethernet1/48.100",
                    "description": "Sub-interface for VLAN 100",
                    "enabled": True,
                    "dot1q_id": 100,
                    "vrf": "PROD",
                    "ipv4_address": "10.10.100.1/24",
                    "ipv6_address": "2001:db8:100::1/64",
                    "mtu": "9216",
                    "speed": "10gb"
                }
            ]
        }
    }