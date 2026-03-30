"""Underlay Multicast Pydantic models."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.common import TimestampMixin, validate_multicast_v4


class UnderlayMulticastCreate(BaseModel):
    """Underlay multicast configuration (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID that this multicast configuration belongs to.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    group_subnet: Optional[str] = Field(
        default="239.1.1.0/25",
        description="IPv4 multicast group range (in CIDR notation) used for the BUM (Broadcast, Unknown Unicast, Multicast) traffic in the underlay.",
        example="239.1.1.0/24",
    )
    rendezvous_points: Optional[Literal[2, 4]] = Field(
        default=2,
        description="Number of Rendezvous Points (RPs) to be configured for Anycast RP. Supported values are 2 or 4.",
        example=2,
    )
    rp_mode: Optional[Literal["asm", "bidir"]] = Field(
        default="asm",
        description="The PIM (Protocol Independent Multicast) mode for the Rendezvous Points. 'asm' (Any-Source Multicast) or 'bidir' (Bidirectional PIM).",
        example="asm",
    )
    underlay_rp_loopback_id: Optional[int] = Field(
        default=254,
        ge=0,
        le=1023,
        description="The interface ID for the RP loopback (e.g., 254 for Loopback254).",
        example=254,
    )
    trm_enable: Optional[bool] = Field(
        default=False,
        description="Whether to enable Tenant Routed Multicast (TRM) for multicast forwarding within VRFs.",
        example=True,
    )
    trm_bgw_msite_enable: Optional[bool] = Field(
        default=False,
        description="Whether to enable TRM across Border Gateways (BGW) in a multisite deployment.",
        example=False,
    )

    @field_validator("group_subnet")
    @classmethod
    def _v4_mcast(cls, v: str | None) -> str | None:
        return validate_multicast_v4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "group_subnet": "239.1.1.0/24",
                    "rendezvous_points": 2,
                    "rp_mode": "asm",
                    "underlay_rp_loopback_id": 254,
                    "trm_enable": True,
                }
            ]
        },
    }


class UnderlayMulticastUpdate(BaseModel):
    """Update underlay multicast config."""

    group_subnet: Optional[str] = Field(
        default=None,
        description="Update the multicast group subnet range.",
        example="239.2.2.0/24",
    )
    rendezvous_points: Optional[Literal[2, 4]] = Field(
        default=None,
        description="Update the number of RPs.",
        example=4,
    )
    rp_mode: Optional[Literal["asm", "bidir"]] = Field(
        default=None,
        description="Update the RP mode.",
        example="bidir",
    )
    underlay_rp_loopback_id: Optional[int] = Field(
        default=None,
        ge=0,
        le=1023,
        description="Update the RP loopback interface ID.",
        example=255,
    )
    trm_enable: Optional[bool] = Field(
        default=None,
        description="Update the TRM enable status.",
        example=True,
    )
    trm_bgw_msite_enable: Optional[bool] = Field(
        default=None,
        description="Update the TRM BGW multisite status.",
        example=True,
    )

    @field_validator("group_subnet")
    @classmethod
    def _v4_mcast(cls, v: str | None) -> str | None:
        return validate_multicast_v4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "group_subnet": "239.2.2.0/24",
                    "trm_enable": True,
                }
            ]
        },
    }


class UnderlayMulticastRead(TimestampMixin):
    """Response body for underlay multicast."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    group_subnet: Optional[str] = Field(
        default=None,
        description="Current multicast group subnet.",
        example="239.1.1.0/24",
    )
    rendezvous_points: Optional[int] = Field(
        default=None,
        description="Current number of RPs.",
        example=2,
    )
    rp_mode: Optional[str] = Field(
        default=None,
        description="Current RP mode.",
        example="asm",
    )
    underlay_rp_loopback_id: Optional[int] = Field(
        default=None,
        description="Current RP loopback ID.",
        example=254,
    )
    trm_enable: Optional[bool] = Field(
        default=None,
        description="Current TRM status.",
        example=True,
    )
    trm_bgw_msite_enable: Optional[bool] = Field(
        default=None,
        description="Current TRM BGW multisite status.",
        example=False,
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "group_subnet": "239.1.1.0/24",
                    "rendezvous_points": 2,
                    "rp_mode": "asm",
                    "underlay_rp_loopback_id": 254,
                    "trm_enable": True,
                    "created_at": "2023-10-27T10:00:00Z",
                    "updated_at": "2023-10-27T10:00:00Z",
                }
            ]
        },
    }
