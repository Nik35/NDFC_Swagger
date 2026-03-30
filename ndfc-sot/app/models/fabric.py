"""Fabric Pydantic models."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


FABRIC_TYPES = Literal[
    "VXLAN_EVPN", "MSD", "MCFG", "ISN", "External", "eBGP_VXLAN"
]


class FabricCreate(BaseModel):
    """Request body to create a fabric."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$",
        description="Unique fabric name.",
        examples=["DC-FABRIC-1"]
    )
    type: FABRIC_TYPES = Field(
        default="VXLAN_EVPN",
        description="Fabric type (VXLAN_EVPN, MSD, MCFG, ISN, External, eBGP_VXLAN).",
        examples=["VXLAN_EVPN"]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "DC-FABRIC-1",
                    "type": "VXLAN_EVPN",
                }
            ]
        }
    }


class FabricUpdate(BaseModel):
    """Request body to update a fabric (partial)."""

    type: Optional[FABRIC_TYPES] = Field(
        default=None,
        description="Fabric type.",
        examples=["eBGP_VXLAN"]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "type": "eBGP_VXLAN",
                }
            ]
        }
    }


class FabricRead(TimestampMixin):
    """Response body for a fabric."""

    name: str = Field(
        description="Fabric name.",
        examples=["DC-FABRIC-1"]
    )
    type: str = Field(
        description="Fabric type.",
        examples=["VXLAN_EVPN"]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
