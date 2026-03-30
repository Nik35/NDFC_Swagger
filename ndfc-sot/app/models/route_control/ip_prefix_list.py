"""IPv4 / IPv6 Prefix List Pydantic models."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.common import TimestampMixin, validate_cidr_v4, validate_cidr


class PrefixListEntry(BaseModel):
    seq_number: int = Field(
        ..., ge=1, le=4294967294, description="Sequence number for this entry.", examples=[10, 20]
    )
    operation: Literal["permit", "deny"] = Field(
        ..., description="Action to take: permit or deny.", examples=["permit"]
    )
    prefix: str = Field(
        ..., description="IPv4 prefix in CIDR notation.", examples=["10.0.0.0/8", "192.168.1.0/24"]
    )
    le: Optional[int] = Field(
        default=None, ge=1, le=32, description="Less-than-or-equal-to mask length.", examples=[32]
    )
    ge: Optional[int] = Field(
        default=None, ge=1, le=32, description="Greater-than-or-equal-to mask length.", examples=[24]
    )
    eq: Optional[int] = Field(
        default=None, ge=1, le=32, description="Exact mask length match.", examples=[24]
    )

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def _ge_le(self) -> "PrefixListEntry":
        if self.ge is not None and self.le is not None and self.ge > self.le:
            raise ValueError("ge must be <= le")
        return self


class Ipv4PrefixListCreate(BaseModel):
    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,62}$", 
        description="Unique name for the IPv4 prefix list.", examples=["IPV4-PREFIX-LIST-1"]
    )
    description: Optional[str] = Field(
        default=None, description="Optional description for the prefix list.", examples=["Allowed internal prefixes"]
    )
    entries: list[PrefixListEntry] = Field(
        ..., min_length=1, description="List of entries defining the prefix matching rules."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "DEFAULT-ONLY",
                    "entries": [{"seq_number": 10, "operation": "permit", "prefix": "0.0.0.0/0"}],
                }
            ]
        }
    }


class Ipv4PrefixListUpdate(BaseModel):
    description: Optional[str] = Field(
        default=None, description="Updated description for the prefix list.", examples=["Updated description"]
    )
    entries: Optional[list[PrefixListEntry]] = Field(
        default=None, min_length=1, description="Updated list of prefix list entries."
    )

    model_config = {"extra": "forbid"}


class Ipv4PrefixListRead(TimestampMixin):
    fabric_id: UUID = Field(description="UUID of the parent fabric.")
    name: str = Field(description="Name of the IPv4 prefix list.")
    description: Optional[str] = Field(default=None, description="Description of the prefix list.")
    entries: list[PrefixListEntry] = Field(default=[], description="List of prefix list entries.")

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }


# IPv6 variants (le/ge up to 128)
class Ipv6PrefixListEntry(BaseModel):
    seq_number: int = Field(
        ..., ge=1, le=4294967294, description="Sequence number for this entry.", examples=[10, 20]
    )
    operation: Literal["permit", "deny"] = Field(
        ..., description="Action to take: permit or deny.", examples=["permit"]
    )
    prefix: str = Field(
        ..., description="IPv6 prefix in CIDR notation.", examples=["2001:db8::/32"]
    )
    le: Optional[int] = Field(
        default=None, ge=1, le=128, description="Less-than-or-equal-to mask length.", examples=[128]
    )
    ge: Optional[int] = Field(
        default=None, ge=1, le=128, description="Greater-than-or-equal-to mask length.", examples=[64]
    )
    eq: Optional[int] = Field(
        default=None, ge=1, le=128, description="Exact mask length match.", examples=[64]
    )

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def _ge_le(self) -> "Ipv6PrefixListEntry":
        if self.ge is not None and self.le is not None and self.ge > self.le:
            raise ValueError("ge must be <= le")
        return self


class Ipv6PrefixListCreate(BaseModel):
    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,62}$", 
        description="Unique name for the IPv6 prefix list.", examples=["IPV6-PREFIX-LIST-1"]
    )
    description: Optional[str] = Field(
        default=None, description="Optional description for the prefix list.", examples=["Allowed IPv6 prefixes"]
    )
    entries: list[Ipv6PrefixListEntry] = Field(
        ..., min_length=1, description="List of entries defining the prefix matching rules."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "IPV6-GUA-ONLY",
                    "entries": [{"seq_number": 10, "operation": "permit", "prefix": "2000::/3", "le": 128}],
                }
            ]
        }
    }


class Ipv6PrefixListUpdate(BaseModel):
    description: Optional[str] = Field(
        default=None, description="Updated description for the prefix list.", examples=["Updated description"]
    )
    entries: Optional[list[Ipv6PrefixListEntry]] = Field(
        default=None, min_length=1, description="Updated list of prefix list entries."
    )

    model_config = {"extra": "forbid"}


class Ipv6PrefixListRead(TimestampMixin):
    fabric_id: UUID = Field(description="UUID of the parent fabric.")
    name: str = Field(description="Name of the IPv6 prefix list.")
    description: Optional[str] = Field(default=None, description="Description of the prefix list.")
    entries: list[Ipv6PrefixListEntry] = Field(default=[], description="List of prefix list entries.")

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }