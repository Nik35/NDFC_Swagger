"""Underlay ISIS Pydantic models."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.common import TimestampMixin


class UnderlayIsisCreate(BaseModel):
    """Underlay ISIS configuration (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID that this IS-IS configuration belongs to.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    authentication_enable: Optional[bool] = Field(
        default=False,
        description="Whether to enable MD5 authentication for IS-IS Hello PDUs and LSPs.",
        example=True,
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="The shared secret key used for IS-IS authentication. Required if authentication_enable is True.",
        example="cisco123",
    )
    authentication_key_id: Optional[int] = Field(
        default=None,
        ge=1,
        le=255,
        description="The ID of the authentication key (1-255).",
        example=1,
    )
    overload_bit: Optional[bool] = Field(
        default=False,
        description="If True, sets the overload bit (OL) in IS-IS LSPs, preventing other routers from using this router for transit traffic.",
        example=False,
    )
    level: Optional[Literal["level-1", "level-2", "level-1-2"]] = Field(
        default="level-2",
        description="The IS-IS level for the routing process. 'level-2' is typically used for the backbone in a single-area design.",
        example="level-2",
    )
    network_type: Optional[Literal["p2p", "broadcast"]] = Field(
        default="p2p",
        description="The network type for IS-IS interfaces. 'p2p' (point-to-point) is recommended for most fabric underlays.",
        example="p2p",
    )

    @model_validator(mode="after")
    def _auth_key_required(self) -> "UnderlayIsisCreate":
        if self.authentication_enable and not self.authentication_key:
            raise ValueError("authentication_key is required when authentication_enable is True")
        return self

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "authentication_enable": True,
                    "authentication_key": "cisco123",
                    "authentication_key_id": 1,
                    "level": "level-2",
                    "network_type": "p2p",
                }
            ]
        },
    }


class UnderlayIsisUpdate(BaseModel):
    """Update underlay IS-IS config."""

    authentication_enable: Optional[bool] = Field(
        default=None,
        description="Update whether IS-IS authentication is enabled.",
        example=True,
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="Update the IS-IS authentication key.",
        example="newsecret456",
    )
    authentication_key_id: Optional[int] = Field(
        default=None,
        ge=1,
        le=255,
        description="Update the IS-IS authentication key ID.",
        example=2,
    )
    overload_bit: Optional[bool] = Field(
        default=None,
        description="Update the IS-IS overload bit status.",
        example=True,
    )
    level: Optional[Literal["level-1", "level-2", "level-1-2"]] = Field(
        default=None,
        description="Update the IS-IS level.",
        example="level-1",
    )
    network_type: Optional[Literal["p2p", "broadcast"]] = Field(
        default=None,
        description="Update the IS-IS network type.",
        example="broadcast",
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "authentication_enable": True,
                    "authentication_key": "newsecret456",
                }
            ]
        },
    }


class UnderlayIsisRead(TimestampMixin):
    """Response body for underlay IS-IS."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    authentication_enable: Optional[bool] = Field(
        default=None,
        description="Current status of IS-IS authentication.",
        example=True,
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="Current IS-IS authentication key.",
        example="cisco123",
    )
    authentication_key_id: Optional[int] = Field(
        default=None,
        description="Current IS-IS authentication key ID.",
        example=1,
    )
    overload_bit: Optional[bool] = Field(
        default=None,
        description="Current status of the IS-IS overload bit.",
        example=False,
    )
    level: Optional[str] = Field(
        default=None,
        description="Current IS-IS level.",
        example="level-2",
    )
    network_type: Optional[str] = Field(
        default=None,
        description="Current IS-IS network type.",
        example="p2p",
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "authentication_enable": True,
                    "authentication_key": "cisco123",
                    "authentication_key_id": 1,
                    "level": "level-2",
                    "network_type": "p2p",
                    "created_at": "2023-10-27T10:00:00Z",
                    "updated_at": "2023-10-27T10:00:00Z",
                }
            ]
        },
    }
