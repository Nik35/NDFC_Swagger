"""Multisite configuration Pydantic models (E.3)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.common import TimestampMixin, validate_ipv4


class MultisiteConfigCreate(BaseModel):
    """Request body to create multisite config (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    enabled: Optional[bool] = Field(
        default=False,
        description="Enable multisite.",
        examples=[True]
    )
    multisite_bgw_ip: Optional[str] = Field(
        default=None,
        description="Multisite BGW IP address.",
        examples=["10.1.1.1"]
    )
    dci_subnet_range: Optional[str] = Field(
        default=None,
        description="DCI subnet range CIDR.",
        examples=["192.168.100.0/24"]
    )
    dci_subnet_mask: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="DCI subnet mask length.",
        examples=[24]
    )
    delay_restore: Optional[int] = Field(
        default=300,
        ge=1,
        le=3600,
        description="Delay restore timer (seconds).",
        examples=[300]
    )

    @field_validator("multisite_bgw_ip")
    @classmethod
    def _validate_ip(cls, v: str | None) -> str | None:
        return validate_ipv4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "enabled": True,
                    "multisite_bgw_ip": "10.1.1.1",
                    "delay_restore": 300,
                }
            ]
        }
    }


class MultisiteConfigUpdate(BaseModel):
    """Update multisite config."""

    enabled: Optional[bool] = Field(
        default=None,
        description="Enable multisite.",
        examples=[False]
    )
    multisite_bgw_ip: Optional[str] = Field(
        default=None,
        description="BGW IP.",
        examples=["10.1.1.2"]
    )
    dci_subnet_range: Optional[str] = Field(
        default=None,
        description="DCI subnet range.",
        examples=["172.16.0.0/24"]
    )
    dci_subnet_mask: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="DCI subnet mask.",
        examples=[24]
    )
    delay_restore: Optional[int] = Field(
        default=None,
        ge=1,
        le=3600,
        description="Delay restore.",
        examples=[600]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "enabled": False,
                    "delay_restore": 600
                }
            ]
        }
    }


class MultisiteConfigRead(TimestampMixin):
    """Response body for multisite config."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    enabled: Optional[bool] = Field(
        default=None,
        description="Multisite enabled.",
        examples=[True]
    )
    multisite_bgw_ip: Optional[str] = Field(
        default=None,
        description="BGW IP.",
        examples=["10.1.1.1"]
    )
    dci_subnet_range: Optional[str] = Field(
        default=None,
        description="DCI subnet range.",
        examples=["192.168.100.0/24"]
    )
    dci_subnet_mask: Optional[int] = Field(
        default=None,
        description="DCI subnet mask.",
        examples=[24]
    )
    delay_restore: Optional[int] = Field(
        default=None,
        description="Delay restore timer.",
        examples=[300]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
