"""Trunk interface Pydantic model."""

from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import Field, field_validator

from app.models.interfaces.base import InterfaceBase, validate_mtu


_VLAN_RANGE_RE = re.compile(
    r"^(\d{1,4}(-\d{1,4})?,)*\d{1,4}(-\d{1,4})?$"
)


def validate_trunk_vlans(v: str) -> str:
    """Validate trunk_allowed_vlans string format, e.g. '100-200,300,400-500'."""
    if not _VLAN_RANGE_RE.match(v):
        raise ValueError(
            f"Invalid trunk_allowed_vlans format: '{v}'. "
            "Expected comma-separated VLAN IDs or ranges (e.g. '100-200,300')."
        )
    return v


class TrunkInterfaceCreate(InterfaceBase):
    """Create a trunk-mode physical interface."""

    mode: Literal["trunk"] = Field(..., description="Interface mode discriminator.", example="trunk")
    name: str = Field(
        ...,
        pattern=r"^(?i)(?:Ethernet|Eth)\d+(?:/\d+){1,2}$",
        description="Physical interface name.",
        example="Ethernet1/5"
    )
    trunk_allowed_vlans: Optional[str] = Field(
        default=None,
        description="Allowed VLAN ranges as string (e.g. '100-200,300').",
        example="100-200,300"
    )
    native_vlan: Optional[int] = Field(
        default=None, ge=1, le=4094, description="Native VLAN ID.", example=1
    )
    mtu: Optional[str] = Field(default=None, description="Maximum Transmission Unit (MTU).", example="9216")
    speed: Optional[Literal["auto", "100mb", "1gb", "10gb", "25gb", "40gb", "100gb"]] = Field(
        default=None, description="Interface speed.", example="10gb"
    )
    spanning_tree_portfast: Optional[bool] = Field(
        default=None, description="Enable spanning-tree portfast.", example=True
    )

    _validate_mtu = field_validator("mtu")(validate_mtu)

    @field_validator("trunk_allowed_vlans")
    @classmethod
    def _validate_vlans(cls, v: str | None) -> str | None:
        return validate_trunk_vlans(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "trunk",
                    "name": "Ethernet1/5",
                    "native_vlan": 1,
                    "trunk_allowed_vlans": "100-200,300",
                    "mtu": "9216",
                    "speed": "10gb",
                    "spanning_tree_portfast": True
                }
            ]
        }
    }
