"""Object Group Pydantic models (E.21)."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class ObjectGroupEntry(BaseModel):
    """A single object group entry. Content varies by group type."""

    ip: Optional[str] = Field(
        default=None, description="IP address or CIDR for 'ip_address' type.", examples=["10.1.1.1/32"]
    )
    network: Optional[str] = Field(
        default=None, description="Network CIDR for 'network' type.", examples=["10.1.1.0/24"]
    )
    port: Optional[str] = Field(
        default=None, description="Port or port range for 'port' type.", examples=["80", "1024-65535"]
    )

    model_config = {"extra": "forbid"}


class ObjectGroupCreate(BaseModel):
    """Create an object group."""

    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, description="Unique name for the object group.", examples=["OG_WEB_SERVERS"]
    )
    type: Literal["ip_address", "network", "port"] = Field(
        ..., description="Type of object group: ip_address, network, or port.", examples=["ip_address"]
    )
    entries: list[ObjectGroupEntry] = Field(
        ..., min_length=1, description="List of entries in the object group."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "OG_SERVERS",
                    "type": "ip_address",
                    "entries": [
                        {"ip": "10.1.1.0/24"},
                    ],
                }
            ]
        }
    }


class ObjectGroupUpdate(BaseModel):
    """Update an object group."""

    entries: Optional[list[ObjectGroupEntry]] = Field(
        default=None, min_length=1, description="Updated list of object group entries."
    )

    model_config = {"extra": "forbid"}


class ObjectGroupRead(TimestampMixin):
    """Response body for an object group."""

    fabric_id: UUID = Field(
        description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        description="Name of the object group.", examples=["OG_WEB_SERVERS"]
    )
    type: str = Field(
        description="Type of object group.", examples=["ip_address"]
    )
    entries: list[ObjectGroupEntry] = Field(
        default=[], description="List of object group entries."
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
