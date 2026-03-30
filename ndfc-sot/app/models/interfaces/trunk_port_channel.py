"""Trunk port-channel Pydantic model."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field, field_validator

from app.models.interfaces.base import InterfaceBase, validate_mtu
from app.models.interfaces.trunk import validate_trunk_vlans


class TrunkPortChannelCreate(InterfaceBase):
    """Create a trunk-mode port-channel."""

    mode: Literal["trunk_port_channel"] = Field(..., description="Interface mode discriminator.", example="trunk_port_channel")
    name: str = Field(..., pattern=r"^[Pp]ort-channel\d+$", description="Port-channel name.", example="Port-channel20")
    trunk_allowed_vlans: Optional[str] = Field(
        default=None,
        description="Allowed VLAN ranges as string (e.g. '100-200,300').",
        example="100-200"
    )
    native_vlan: Optional[int] = Field(default=None, ge=1, le=4094, description="Native VLAN ID.", example=1)
    vpc_id: Optional[int] = Field(default=None, ge=1, le=4096, description="Virtual Port-Channel (vPC) ID.", example=20)
    pc_mode: Optional[Literal["active", "passive", "on"]] = Field(default="active", description="Port-channel LACP mode.", example="active")
    members: Optional[list[str]] = Field(default=None, description="Member physical interfaces.", example=["Ethernet1/20", "Ethernet1/21"])
    mtu: Optional[str] = Field(default=None, description="Maximum Transmission Unit (MTU).", example="9216")
    spanning_tree_portfast: Optional[bool] = Field(default=None, description="Enable spanning-tree portfast.", example=True)

    _validate_mtu = field_validator("mtu")(validate_mtu)

    @field_validator("trunk_allowed_vlans")
    @classmethod
    def _validate_vlans(cls, v: str | None) -> str | None:
        return validate_trunk_vlans(v) if v else v

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
                    "mode": "trunk_port_channel",
                    "name": "Port-channel20",
                    "vpc_id": 20,
                    "trunk_allowed_vlans": "100-200",
                    "members": ["Ethernet1/20", "Ethernet1/21"],
                    "mtu": "9216",
                    "pc_mode": "active",
                    "spanning_tree_portfast": True
                }
            ]
        }
    }
