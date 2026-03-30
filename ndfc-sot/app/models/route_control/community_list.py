"""Community List Pydantic models."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class StandardCommunityListEntry(BaseModel):
    seq_number: int = Field(
        ..., ge=1, description="Sequence number of the entry.", examples=[10, 20]
    )
    operation: Literal["permit", "deny"] = Field(
        ..., description="Action to take: permit or deny.", examples=["permit"]
    )
    communities: list[str] = Field(
        ..., min_length=1,
        description="Community values in AA:NN format or keywords (no-export, no-advertise, internet, local-AS, no-peer).",
        examples=[["65001:100"], ["internet", "no-export"]]
    )

    model_config = {"extra": "forbid"}


class StandardCommunityListCreate(BaseModel):
    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, description="Unique name for the community list.", examples=["ALLOW-COMM"]
    )
    entries: list[StandardCommunityListEntry] = Field(
        ..., min_length=1, description="List of standard community list entries."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "ALLOW-COMM",
                    "entries": [
                        {"seq_number": 10, "operation": "permit", "communities": ["65001:100"]}
                    ]
                }
            ]
        }
    }


class StandardCommunityListUpdate(BaseModel):
    entries: Optional[list[StandardCommunityListEntry]] = Field(
        default=None, min_length=1, description="Updated list of standard community list entries."
    )

    model_config = {"extra": "forbid"}


class StandardCommunityListRead(TimestampMixin):
    fabric_id: UUID = Field(description="UUID of the parent fabric.")
    name: str = Field(description="Name of the community list.")
    entries: list[StandardCommunityListEntry] = Field(
        default=[], description="List of standard community list entries."
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }


# Extended community
class ExtendedCommunities(BaseModel):
    four_byte_as_generic: Optional[list[str]] = Field(
        default=None, description="4-byte AS generic extended communities.", examples=[["123456:100"]]
    )
    rmac: Optional[list[str]] = Field(
        default=None, description="Router MAC extended communities.", examples=[["0000.1111.2222"]]
    )
    rt: Optional[list[str]] = Field(
        default=None, description="Route target extended communities.", examples=[["65001:100"]]
    )
    soo: Optional[list[str]] = Field(
        default=None, description="Site of origin extended communities.", examples=[["65001:200"]]
    )

    model_config = {"extra": "forbid"}


class ExtendedCommunityListEntry(BaseModel):
    seq_number: int = Field(
        ..., ge=1, description="Sequence number of the entry.", examples=[10, 20]
    )
    operation: Literal["permit", "deny"] = Field(
        ..., description="Action to take: permit or deny.", examples=["permit"]
    )
    communities: ExtendedCommunities = Field(
        ..., description="Extended community values."
    )

    model_config = {"extra": "forbid"}


class ExtendedCommunityListCreate(BaseModel):
    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, description="Unique name for the extended community list.", examples=["EXT-COMM-1"]
    )
    entries: list[ExtendedCommunityListEntry] = Field(
        ..., min_length=1, description="List of extended community list entries."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "EXT-COMM-1",
                    "entries": [
                        {
                            "seq_number": 10,
                            "operation": "permit",
                            "communities": {"rt": ["65001:100"]}
                        }
                    ]
                }
            ]
        }
    }


class ExtendedCommunityListUpdate(BaseModel):
    entries: Optional[list[ExtendedCommunityListEntry]] = Field(
        default=None, min_length=1, description="Updated list of extended community list entries."
    )

    model_config = {"extra": "forbid"}


class ExtendedCommunityListRead(TimestampMixin):
    fabric_id: UUID = Field(description="UUID of the parent fabric.")
    name: str = Field(description="Name of the extended community list.")
    entries: list[ExtendedCommunityListEntry] = Field(
        default=[], description="List of extended community list entries."
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }