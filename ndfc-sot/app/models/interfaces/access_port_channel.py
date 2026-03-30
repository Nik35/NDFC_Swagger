"""Access port-channel Pydantic model."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field, field_validator

from app.models.interfaces.base import InterfaceBase, validate_mtu


class AccessPortChannelCreate(InterfaceBase):
    """Create an access-mode port-channel."""

    mode: Literal["access_port_channel"] = Field(..., description="Interface mode discriminator.", example="access_port_channel")
    name: str = Field(
        ...,
        pattern=r"^[Pp]ort-channel\d+$",
        description="Port-channel name (e.g. Port-channel10).",
        example="Port-channel10"
    )
    access_vlan: Optional[int] = Field(default=None, ge=1, le=4094, description="Access VLAN ID.", example=100)
    vpc_id: Optional[int] = Field(default=None, ge=1, le=4096, description="vPC ID.", example=10)
    pc_mode: Optional[Literal["active", "passive", "on"]] = Field(default="active", description="LACP mode.", example="active")
    members: Optional[list[str]] = Field(default=None, description="Member physical interfaces.", example=["Ethernet1/10", "Ethernet1/11"])
    mtu: Optional[str] = Field(default=None, description="MTU.", example="9216")
    speed: Optional[Literal["auto", "100mb", "1gb", "10gb", "25gb", "40gb", "100gb"]] = Field(
        default=None, description="Interface speed.", example="10gb"
    )

    _validate_mtu = field_validator("mtu")(validate_mtu)

    @field_validator("members")
    @classmethod
    def _validate_members(cls, v: list[str] | None) -> list[str] | None:
        if v:
            import re
            pat = re.compile(r"^(?i)(?:Ethernet|Eth)\d+(?:/\d+){1,2}$")
            for m in v:
                if not pat.match(m):
                    raise ValueError(f"Member '{m}' is not a valid physical interface name")
        return v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "access_port_channel",
                    "name": "Port-channel10",
                    "description": "Port-channel to server",
                    "enabled": True,
                    "access_vlan": 100,
                    "vpc_id": 10,
                    "pc_mode": "active",
                    "members": ["Ethernet1/10", "Ethernet1/11"],
                    "mtu": "9216",
                    "speed": "10gb"
                }
            ]
        }
    }