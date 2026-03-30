"""Underlay General Pydantic models (E.10)."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class UnderlayGeneralCreate(BaseModel):
    """Underlay general configuration (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    replication_mode: Optional[Literal["multicast", "ingress"]] = Field(
        default="multicast",
        description="Replication mode.",
        example="multicast"
    )
    enable_trm: Optional[bool] = Field(
        default=False,
        description="Enable Tenant Routed Multicast.",
        example=False
    )
    underlay_routing_protocol: Optional[Literal["ospf", "is-is"]] = Field(
        default="ospf",
        description="Underlay routing protocol.",
        example="ospf"
    )
    link_state_routing_tag: Optional[str] = Field(
        default="UNDERLAY",
        description="Routing tag for underlay.",
        example="UNDERLAY"
    )
    enable_pvlan: Optional[bool] = Field(
        default=False,
        description="Enable Private VLAN.",
        example=False
    )
    enable_netflow: Optional[bool] = Field(
        default=False,
        description="Enable NetFlow.",
        example=True
    )
    stp_root_bridge_option: Optional[Literal["unmanaged", "rpvst+", "mst"]] = Field(
        default="unmanaged",
        description="STP root bridge option.",
        example="unmanaged"
    )
    brownfield_import: Optional[bool] = Field(
        default=False,
        description="Enable brownfield import.",
        example=False
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "replication_mode": "multicast",
                    "enable_trm": False,
                    "underlay_routing_protocol": "ospf",
                }
            ]
        }
    }


class UnderlayGeneralUpdate(BaseModel):
    """Update underlay general config."""

    replication_mode: Optional[Literal["multicast", "ingress"]] = Field(
        default=None,
        description="Replication mode.",
        example="ingress"
    )
    enable_trm: Optional[bool] = Field(
        default=None,
        description="Enable TRM.",
        example=True
    )
    underlay_routing_protocol: Optional[Literal["ospf", "is-is"]] = Field(
        default=None,
        description="Routing protocol.",
        example="is-is"
    )
    link_state_routing_tag: Optional[str] = Field(
        default=None,
        description="Routing tag.",
        example="GLOBAL-UNDERLAY"
    )
    enable_pvlan: Optional[bool] = Field(
        default=None,
        description="Enable PVLAN.",
        example=True
    )
    enable_netflow: Optional[bool] = Field(
        default=None,
        description="Enable NetFlow.",
        example=False
    )
    stp_root_bridge_option: Optional[Literal["unmanaged", "rpvst+", "mst"]] = Field(
        default=None,
        description="STP option.",
        example="mst"
    )
    brownfield_import: Optional[bool] = Field(
        default=None,
        description="Brownfield import.",
        example=True
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "replication_mode": "ingress",
                    "underlay_routing_protocol": "is-is"
                }
            ]
        }
    }


class UnderlayGeneralRead(TimestampMixin):
    """Response body for underlay general config."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    replication_mode: Optional[str] = Field(
        default=None,
        description="Replication mode.",
        example="multicast"
    )
    enable_trm: Optional[bool] = Field(
        default=None,
        description="TRM enabled.",
        example=False
    )
    underlay_routing_protocol: Optional[str] = Field(
        default=None,
        description="Routing protocol.",
        example="ospf"
    )
    link_state_routing_tag: Optional[str] = Field(
        default=None,
        description="Routing tag.",
        example="UNDERLAY"
    )
    enable_pvlan: Optional[bool] = Field(
        default=None,
        description="PVLAN enabled.",
        example=False
    )
    enable_netflow: Optional[bool] = Field(
        default=None,
        description="NetFlow enabled.",
        example=True
    )
    stp_root_bridge_option: Optional[str] = Field(
        default=None,
        description="STP option.",
        example="unmanaged"
    )
    brownfield_import: Optional[bool] = Field(
        default=None,
        description="Brownfield import.",
        example=False
    )

    model_config = {"from_attributes": True}
