"""Dot1Q Tunnel interface Pydantic model."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field

from app.models.interfaces.base import InterfaceBase


class Dot1qTunnelInterfaceCreate(InterfaceBase):
    """Create a Dot1Q tunnel interface."""

    mode: Literal["dot1q_tunnel"] = Field(..., description="Interface mode discriminator.", example="dot1q_tunnel")
    name: str = Field(
        ...,
        pattern=r"^(?i)(?:Ethernet|Eth)\d+(?:/\d+){1,2}$",
        description="Physical interface name (e.g. Ethernet1/10).",
        example="Ethernet1/10"
    )
    tunnel_vlan: int = Field(
        ..., ge=1, le=4094, description="Outer 802.1Q tunnel VLAN ID.", example=500
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "dot1q_tunnel",
                    "name": "Ethernet1/10",
                    "tunnel_vlan": 500,
                    "description": "L2 Tunnel for Customer A",
                    "enabled": True
                }
            ]
        }
    }
