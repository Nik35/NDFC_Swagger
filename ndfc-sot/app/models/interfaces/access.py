"""Access interface Pydantic model."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field, field_validator

from app.models.interfaces.base import InterfaceBase, SPEED_CHOICES, validate_mtu


class AccessInterfaceCreate(InterfaceBase):
    """Create an access-mode physical interface."""

    mode: Literal["access"] = Field(..., description="Interface mode discriminator.", example="access")
    name: str = Field(
        ...,
        pattern=r"^(?i)(?:Ethernet|Eth)\d+(?:/\d+){1,2}$",
        description="Physical interface name (e.g. Ethernet1/1).",
        example="Ethernet1/10"
    )
    access_vlan: Optional[int] = Field(default=None, ge=1, le=4094, description="Access VLAN ID.", example=100)
    mtu: Optional[str] = Field(default=None, description="Maximum Transmission Unit (MTU).", example="9216")
    speed: Optional[Literal["auto", "100mb", "1gb", "10gb", "25gb", "40gb", "100gb"]] = Field(
        default=None, description="Interface speed.", example="10gb"
    )
    duplex: Optional[Literal["auto", "full", "half"]] = Field(default=None, description="Interface duplex mode.", example="full")
    spanning_tree_portfast: Optional[bool] = Field(default=None, description="Enable spanning-tree portfast.", example=True)

    _validate_mtu = field_validator("mtu")(validate_mtu)

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "access",
                    "name": "Ethernet1/10",
                    "access_vlan": 100,
                    "description": "Server port",
                    "enabled": True,
                    "spanning_tree_portfast": True,
                    "mtu": "9216",
                    "speed": "10gb",
                    "duplex": "full"
                }
            ]
        }
    }
