"""AS-Path Access List Pydantic models."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class IpAsPathAccessListEntry(BaseModel):
    seq_number: int = Field(
        ..., ge=1, description="Sequence number of the entry.", examples=[10, 20]
    )
    operation: Literal["permit", "deny"] = Field(
        ..., description="Action to take: permit or deny.", examples=["permit"]
    )
    bgp_as_paths_regex: str = Field(
        ..., description="BGP AS-path regular expression.", examples=["^$", "_65001$", "100 200"]
    )

    model_config = {"extra": "forbid"}


class IpAsPathAccessListCreate(BaseModel):
    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, description="Unique name for the AS-path access list.", examples=["AS-PATH-LIST-1"]
    )
    entries: list[IpAsPathAccessListEntry] = Field(
        ..., min_length=1, description="List of entries defining the AS-path matching rules."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "LOCAL-ONLY",
                    "entries": [
                        {"seq_number": 10, "operation": "permit", "bgp_as_paths_regex": "^$"}
                    ],
                }
            ]
        }
    }


class IpAsPathAccessListUpdate(BaseModel):
    entries: Optional[list[IpAsPathAccessListEntry]] = Field(
        default=None, min_length=1, description="Updated list of AS-path access list entries."
    )

    model_config = {"extra": "forbid"}


class IpAsPathAccessListRead(TimestampMixin):
    fabric_id: UUID = Field(description="UUID of the parent fabric.")
    name: str = Field(description="Name of the AS-path access list.")
    entries: list[IpAsPathAccessListEntry] = Field(
        default=[], description="List of AS-path access list entries."
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }