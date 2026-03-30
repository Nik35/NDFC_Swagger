"""Underlay BGP Pydantic models (E.15)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.common import TimestampMixin


class UnderlayBgpCreate(BaseModel):
    """Underlay BGP configuration (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    authentication_enable: Optional[bool] = Field(
        default=False,
        description="Enable BGP authentication.",
        example=True
    )
    authentication_key_type: Optional[int] = Field(
        default=3,
        ge=3,
        le=7,
        description="Authentication key type.",
        example=3
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="BGP authentication key.",
        example="v3ry-53cr3t"
    )

    @model_validator(mode="after")
    def _auth_key_required(self) -> "UnderlayBgpCreate":
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
                    "authentication_key_type": 3,
                    "authentication_key": "v3ry-53cr3t"
                }
            ]
        }
    }


class UnderlayBgpUpdate(BaseModel):
    """Update underlay BGP config."""

    authentication_enable: Optional[bool] = Field(
        default=None,
        description="BGP auth enable.",
        example=False
    )
    authentication_key_type: Optional[int] = Field(
        default=None,
        ge=3,
        le=7,
        description="Auth key type.",
        example=7
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="Auth key.",
        example="n3w-53cr3t"
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "authentication_enable": False
                }
            ]
        }
    }


class UnderlayBgpRead(TimestampMixin):
    """Response body for underlay BGP."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    authentication_enable: Optional[bool] = Field(
        default=None,
        description="Auth enable.",
        example=True
    )
    authentication_key_type: Optional[int] = Field(
        default=None,
        description="Auth key type.",
        example=3
    )
    authentication_key: Optional[str] = Field(
        default=None,
        description="Auth key.",
        example="v3ry-53cr3t"
    )

    model_config = {"from_attributes": True}
