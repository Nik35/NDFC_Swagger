"""Routed interface Pydantic model."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field, field_validator

from app.models.common import validate_cidr
from app.models.interfaces.base import InterfaceBase, validate_mtu


class RoutedInterfaceCreate(InterfaceBase):
    """Create a routed (L3) physical interface."""

    mode: Literal["routed"] = Field(..., description="Interface mode discriminator.", example="routed")
    name: str = Field(
        ...,
        pattern=r"^(?i)(?:Ethernet|Eth)\d+(?:/\d+){1,2}$",
        description="Physical interface name (e.g. Ethernet1/48).",
        example="Ethernet1/48"
    )
    vrf: Optional[str] = Field(default=None, description="VRF name.", example="PROD")
    ipv4_address: Optional[str] = Field(default=None, description="IPv4 CIDR.", example="10.10.10.1/30")
    ipv6_address: Optional[str] = Field(default=None, description="IPv6 CIDR.", example="2001:db8:10::1/126")
    mtu: Optional[str] = Field(default=None, description="MTU.", example="9216")
    speed: Optional[Literal["auto", "100mb", "1gb", "10gb", "25gb", "40gb", "100gb"]] = Field(
        default=None, description="Interface speed.", example="10gb"
    )
    ipv4_route_tag: Optional[int] = Field(default=None, description="Route tag.", example=100)
    route_map_tag: Optional[str] = Field(default=None, description="Route-map name.", example="RM_PROD")
    ospf_area: Optional[str] = Field(default=None, description="OSPF area ID.", example="0.0.0.0")
    ospf_auth_enable: Optional[bool] = Field(default=None, description="Enable OSPF authentication.", example=True)
    ospf_auth_key: Optional[str] = Field(default=None, description="OSPF authentication key.", example="cisco123")

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
                    "mode": "routed",
                    "name": "Ethernet1/48",
                    "description": "L3 link to Core",
                    "enabled": True,
                    "vrf": "PROD",
                    "ipv4_address": "10.10.10.1/30",
                    "ipv6_address": "2001:db8:10::1/126",
                    "mtu": "9216",
                    "speed": "10gb",
                    "ospf_area": "0.0.0.0",
                    "ospf_auth_enable": True,
                    "ospf_auth_key": "cisco123"
                }
            ]
        }
    }
