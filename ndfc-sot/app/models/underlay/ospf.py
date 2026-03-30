"""Underlay OSPF Pydantic models (E.14)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.common import TimestampMixin


class UnderlayOspfCreate(BaseModel):
    """Underlay OSPF configuration (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID that this OSPF configuration belongs to.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    area_id: Optional[str] = Field(
        default="0.0.0.0",
        description="The OSPF area ID in dotted-decimal format. Area 0.0.0.0 is the backbone area.",
        example="0.0.0.0",
    )
    authentication_enable: Optional[bool] = Field(
        default=False,
        description="Whether to enable MD5 authentication for OSPF packets.",
        example=True,
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="The shared secret key used for OSPF authentication. Required if authentication_enable is True.",
        example="cisco_ospf_key",
    )
    authentication_key_id: Optional[int] = Field(
        default=None,
        ge=1,
        le=255,
        description="The ID of the OSPF authentication key (1-255).",
        example=1,
    )

    @model_validator(mode="after")
    def _auth_key_required(self) -> "UnderlayOspfCreate":
        if self.authentication_enable and not self.authentication_key:
            raise ValueError("authentication_key is required when authentication_enable is True")
        return self

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "area_id": "0.0.0.0",
                    "authentication_enable": True,
                    "authentication_key": "cisco_ospf_key",
                    "authentication_key_id": 1,
                }
            ]
        },
    }


class UnderlayOspfUpdate(BaseModel):
    """Update underlay OSPF config."""

    area_id: Optional[str] = Field(
        default=None,
        description="Update the OSPF area ID.",
        example="0.0.0.1",
    )
    authentication_enable: Optional[bool] = Field(
        default=None,
        description="Update whether OSPF authentication is enabled.",
        example=True,
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="Update the OSPF authentication key.",
        example="new_ospf_secret",
    )
    authentication_key_id: Optional[int] = Field(
        default=None,
        ge=1,
        le=255,
        description="Update the OSPF authentication key ID.",
        example=10,
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "authentication_enable": True,
                    "authentication_key": "new_ospf_secret",
                }
            ]
        },
    }


class UnderlayOspfRead(TimestampMixin):
    """Response body for underlay OSPF."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    area_id: Optional[str] = Field(
        default=None,
        description="Current OSPF area ID.",
        example="0.0.0.0",
    )
    authentication_enable: Optional[bool] = Field(
        default=None,
        description="Current OSPF authentication status.",
        example=True,
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="Current OSPF authentication key.",
        example="cisco_ospf_key",
    )
    authentication_key_id: Optional[int] = Field(
        default=None,
        description="Current OSPF authentication key ID.",
        example=1,
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "area_id": "0.0.0.0",
                    "authentication_enable": True,
                    "authentication_key": "cisco_ospf_key",
                    "authentication_key_id": 1,
                    "created_at": "2023-10-27T10:00:00Z",
                    "updated_at": "2023-10-27T10:00:00Z",
                }
            ]
        },
    }
