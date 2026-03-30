"""IP ACL Pydantic models (E.21)."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class IpAclEntry(BaseModel):
    """A single ACL entry."""

    sequence: int = Field(
        ..., ge=1, le=4294967294, description="Sequence number for this entry.", examples=[10, 20]
    )
    action: Literal["permit", "deny"] = Field(
        ..., description="Action to take: permit or deny.", examples=["permit"]
    )
    protocol: Optional[str] = Field(
        default=None, description="IP protocol to match (e.g., ip, tcp, udp, icmp).", examples=["tcp", "udp"]
    )
    source: Optional[str] = Field(
        default=None, description="Source address (any, host x.x.x.x, or CIDR).", examples=["10.1.1.0/24", "any"]
    )
    source_port: Optional[str] = Field(
        default=None, description="Source port or range (e.g., 80, 1024-65535).", examples=["any", "80"]
    )
    destination: Optional[str] = Field(
        default=None, description="Destination address (any, host x.x.x.x, or CIDR).", examples=["192.168.1.0/24", "host 1.1.1.1"]
    )
    destination_port: Optional[str] = Field(
        default=None, description="Destination port or range (e.g., 443, eq 22).", examples=["443", "range 1000 2000"]
    )
    dscp: Optional[int] = Field(
        default=None, ge=0, le=63, description="DSCP value to match (0-63).", examples=[46]
    )
    time_range: Optional[str] = Field(
        default=None, description="Name of the time-range to apply to this entry.", examples=["OFFICE-HOURS"]
    )

    model_config = {"extra": "forbid"}


class IpAclCreate(BaseModel):
    """Create an IP ACL."""

    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, description="Unique name for the IP ACL.", examples=["ACL_WEB_TRAFFIC"]
    )
    type: Literal["standard", "extended"] = Field(
        ..., description="Type of ACL: standard or extended.", examples=["extended"]
    )
    entries: list[IpAclEntry] = Field(
        ..., min_length=1, description="List of entries defining the ACL rules."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "ACL_PERMIT_ALL",
                    "type": "extended",
                    "entries": [
                        {
                            "sequence": 10,
                            "action": "permit",
                            "protocol": "ip",
                            "source": "any",
                            "destination": "any",
                        }
                    ],
                }
            ]
        }
    }


class IpAclUpdate(BaseModel):
    """Update an IP ACL."""

    entries: Optional[list[IpAclEntry]] = Field(
        default=None, min_length=1, description="Updated list of ACL entries."
    )

    model_config = {"extra": "forbid"}


class IpAclRead(TimestampMixin):
    """Response body for an IP ACL."""

    fabric_id: UUID = Field(
        description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        description="Name of the IP ACL.", examples=["ACL_WEB_TRAFFIC"]
    )
    type: str = Field(
        description="Type of ACL.", examples=["extended"]
    )
    entries: list[IpAclEntry] = Field(
        default=[], description="List of ACL entries."
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
