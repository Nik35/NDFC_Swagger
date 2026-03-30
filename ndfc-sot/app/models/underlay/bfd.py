"""Underlay BFD Pydantic models (E.16)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class UnderlayBfdCreate(BaseModel):
    """Underlay BFD configuration (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    enable: Optional[bool] = Field(
        default=False,
        description="Enable BFD globally.",
        example=True
    )
    min_tx: Optional[int] = Field(
        default=50,
        ge=50,
        le=999,
        description="BFD min TX interval (ms).",
        example=50
    )
    min_rx: Optional[int] = Field(
        default=50,
        ge=50,
        le=999,
        description="BFD min RX interval (ms).",
        example=50
    )
    multiplier: Optional[int] = Field(
        default=3,
        ge=1,
        le=50,
        description="BFD detection multiplier.",
        example=3
    )
    enable_ibgp: Optional[bool] = Field(
        default=False,
        description="Enable BFD for iBGP.",
        example=True
    )
    enable_ospf: Optional[bool] = Field(
        default=False,
        description="Enable BFD for OSPF.",
        example=True
    )
    enable_isis: Optional[bool] = Field(
        default=False,
        description="Enable BFD for IS-IS.",
        example=False
    )
    enable_pim: Optional[bool] = Field(
        default=False,
        description="Enable BFD for PIM.",
        example=True
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "enable": True,
                    "min_tx": 50,
                    "min_rx": 50,
                    "multiplier": 3,
                    "enable_ibgp": True,
                    "enable_ospf": True
                }
            ]
        }
    }


class UnderlayBfdUpdate(BaseModel):
    """Update underlay BFD config."""

    enable: Optional[bool] = Field(
        default=None,
        description="Enable BFD.",
        example=False
    )
    min_tx: Optional[int] = Field(
        default=None,
        ge=50,
        le=999,
        description="Min TX.",
        example=100
    )
    min_rx: Optional[int] = Field(
        default=None,
        ge=50,
        le=999,
        description="Min RX.",
        example=100
    )
    multiplier: Optional[int] = Field(
        default=None,
        ge=1,
        le=50,
        description="Multiplier.",
        example=5
    )
    enable_ibgp: Optional[bool] = Field(
        default=None,
        description="BFD for iBGP.",
        example=False
    )
    enable_ospf: Optional[bool] = Field(
        default=None,
        description="BFD for OSPF.",
        example=False
    )
    enable_isis: Optional[bool] = Field(
        default=None,
        description="BFD for IS-IS.",
        example=True
    )
    enable_pim: Optional[bool] = Field(
        default=None,
        description="BFD for PIM.",
        example=False
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "min_tx": 100,
                    "min_rx": 100,
                    "multiplier": 5
                }
            ]
        }
    }


class UnderlayBfdRead(TimestampMixin):
    """Response body for underlay BFD."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    enable: Optional[bool] = Field(
        default=None,
        description="BFD enabled.",
        example=True
    )
    min_tx: Optional[int] = Field(
        default=None,
        description="Min TX.",
        example=50
    )
    min_rx: Optional[int] = Field(
        default=None,
        description="Min RX.",
        example=50
    )
    multiplier: Optional[int] = Field(
        default=None,
        description="Multiplier.",
        example=3
    )
    enable_ibgp: Optional[bool] = Field(
        default=None,
        description="BFD for iBGP.",
        example=True
    )
    enable_ospf: Optional[bool] = Field(
        default=None,
        description="BFD for OSPF.",
        example=True
    )
    enable_isis: Optional[bool] = Field(
        default=None,
        description="BFD for IS-IS.",
        example=False
    )
    enable_pim: Optional[bool] = Field(
        default=None,
        description="BFD for PIM.",
        example=True
    )

    model_config = {"from_attributes": True}
