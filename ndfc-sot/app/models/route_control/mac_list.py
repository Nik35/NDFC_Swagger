"""MAC List Pydantic models (E.21)."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class MacListEntry(BaseModel):
    """A single MAC list entry."""

    sequence: int = Field(
        ..., ge=1, le=4294967294, description="Sequence number for this entry.", examples=[10, 20]
    )
    action: Literal["permit", "deny"] = Field(
        ..., description="Action to take: permit or deny.", examples=["permit"]
    )
    mac_address: str = Field(
        ..., description="MAC address in HHHH.HHHH.HHHH format.", examples=["0000.0000.0000", "aaaa.bbbb.cccc"]
    )
    mask: Optional[str] = Field(
        default=None, description="MAC mask in HHHH.HHHH.HHHH format.", examples=["ffff.ffff.ffff", "ffff.ffff.0000"]
    )

    model_config = {"extra": "forbid"}


class MacListCreate(BaseModel):
    """Create a MAC list."""

    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, description="Unique name for the MAC list.", examples=["MAC_FILTER_1"]
    )
    entries: list[MacListEntry] = Field(
        ..., min_length=1, description="List of entries defining the MAC matching rules."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "MAC_FILTER",
                    "entries": [
                        {
                            "sequence": 10,
                            "action": "permit",
                            "mac_address": "0000.0000.0000",
                            "mask": "ffff.ffff.ffff",
                        }
                    ],
                }
            ]
        }
    }


class MacListUpdate(BaseModel):
    """Update a MAC list."""

    entries: Optional[list[MacListEntry]] = Field(
        default=None, min_length=1, description="Updated list of MAC list entries."
    )

    model_config = {"extra": "forbid"}


class MacListRead(TimestampMixin):
    """Response body for a MAC list."""

    fabric_id: UUID = Field(
        description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        description="Name of the MAC list.", examples=["MAC_FILTER_1"]
    )
    entries: list[MacListEntry] = Field(
        default=[], description="List of MAC list entries."
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
