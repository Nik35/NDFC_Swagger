"""Breakout interface Pydantic model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.models.interfaces.base import InterfaceBase


class BreakoutInterfaceCreate(InterfaceBase):
    """Create a breakout interface."""

    mode: Literal["breakout"] = Field(..., description="Interface mode discriminator.", example="breakout")
    name: str = Field(
        ...,
        pattern=r"^(?i)(?:Ethernet|Eth)\d+(?:/\d+){1,2}$",
        description="Physical interface name (e.g. Ethernet1/49).",
        example="Ethernet1/49"
    )
    breakout_mode: str = Field(
        ...,
        description="Breakout mode (e.g. '10g-4x', '25g-4x').",
        example="10g-4x"
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "breakout",
                    "name": "Ethernet1/49",
                    "breakout_mode": "10g-4x",
                    "description": "Breakout for 10G links",
                    "enabled": True
                }
            ]
        }
    }
