"""Route Map Pydantic models."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


class RouteMapMatchIpv4(BaseModel):
    address_prefix_list: Optional[list[str]] = Field(
        default=None, description="Names of IPv4 prefix-lists to match.", examples=[["PREFIX-LIST-1"]]
    )
    next_hop_prefix_list: Optional[list[str]] = Field(
        default=None, description="Names of next-hop IPv4 prefix-lists to match.", examples=[["NH-PREFIX-LIST"]]
    )

    model_config = {"extra": "forbid"}


class RouteMapMatchIpv6(BaseModel):
    address_prefix_list: Optional[list[str]] = Field(
        default=None, description="Names of IPv6 prefix-lists to match.", examples=[["IPV6-PREFIX-LIST-1"]]
    )
    next_hop_prefix_list: Optional[list[str]] = Field(
        default=None, description="Names of next-hop IPv6 prefix-lists to match.", examples=[["IPV6-NH-PREFIX-LIST"]]
    )

    model_config = {"extra": "forbid"}


class RouteMapMatch(BaseModel):
    as_path_list: Optional[list[str]] = Field(
        default=None, description="Names of AS-path access-lists to match.", examples=[["AS-PATH-LIST-1"]]
    )
    community_list: Optional[list[str]] = Field(
        default=None, description="Names of community lists to match.", examples=[["COMM-LIST-1"]]
    )
    extended_community_list: Optional[list[str]] = Field(
        default=None, description="Names of extended community lists to match.", examples=[["EXT-COMM-LIST-1"]]
    )
    ipv4: Optional[RouteMapMatchIpv4] = Field(
        default=None, description="IPv4-specific match criteria."
    )
    ipv6: Optional[RouteMapMatchIpv6] = Field(
        default=None, description="IPv6-specific match criteria."
    )
    interfaces: Optional[list[str]] = Field(
        default=None, description="Names of interfaces to match.", examples=[["Ethernet1/1"]]
    )
    metric: Optional[list[int]] = Field(
        default=None, description="Metric values to match.", examples=[[100, 200]]
    )
    tag: Optional[list[int]] = Field(
        default=None, description="Route tag values to match.", examples=[[65001]]
    )
    route_types: Optional[list[Literal[
        "external", "internal", "level-1", "level-2", "local",
        "nssa-external", "type-1", "type-2",
    ]]] = Field(
        default=None, description="Route types to match.", examples=[["external", "internal"]]
    )

    model_config = {"extra": "forbid"}


class RouteMapSetAsPath(BaseModel):
    prepend: Optional[list[str]] = Field(
        default=None, description="AS numbers to prepend to the AS-path.", examples=[["65001", "65001"]]
    )
    tag: Optional[bool] = Field(
        default=None, description="Whether to set the AS-path tag.", examples=[True]
    )

    model_config = {"extra": "forbid"}


class RouteMapSetCommunity(BaseModel):
    communities: Optional[list[str]] = Field(
        default=None, description="Community values to set (AA:NN or keywords).", examples=[["65001:100", "no-export"]]
    )
    additive: Optional[bool] = Field(
        default=None, description="Whether to add communities to existing ones.", examples=[True]
    )
    no_community: Optional[bool] = Field(
        default=None, description="Whether to remove all communities.", examples=[False]
    )

    model_config = {"extra": "forbid"}


class RouteMapSetExtCommunity(BaseModel):
    rt: Optional[list[str]] = Field(
        default=None, description="Route targets to set.", examples=[["65001:100"]]
    )
    soo: Optional[list[str]] = Field(
        default=None, description="Site-of-origin values to set.", examples=[["65001:200"]]
    )
    additive: Optional[bool] = Field(
        default=None, description="Whether to add extended communities to existing ones.", examples=[True]
    )

    model_config = {"extra": "forbid"}


class RouteMapSet(BaseModel):
    as_path: Optional[RouteMapSetAsPath] = Field(
        default=None, description="AS-path manipulation actions."
    )
    community: Optional[RouteMapSetCommunity] = Field(
        default=None, description="Community manipulation actions."
    )
    extended_community: Optional[RouteMapSetExtCommunity] = Field(
        default=None, description="Extended community manipulation actions."
    )
    metric: Optional[int] = Field(
        default=None, description="Metric value to set.", examples=[100]
    )
    local_preference: Optional[int] = Field(
        default=None, ge=0, le=4294967295, description="Local preference value to set.", examples=[200]
    )
    weight: Optional[int] = Field(
        default=None, ge=0, le=65535, description="Weight value to set.", examples=[300]
    )
    origin: Optional[Literal["igp", "egp", "incomplete"]] = Field(
        default=None, description="Origin attribute to set.", examples=["igp"]
    )
    next_hop: Optional[str] = Field(
        default=None, description="IPv4 next-hop address to set.", examples=["10.1.1.1"]
    )
    ipv6_next_hop: Optional[str] = Field(
        default=None, description="IPv6 next-hop address to set.", examples=["2001:db8::1"]
    )

    model_config = {"extra": "forbid"}


class RouteMapEntry(BaseModel):
    seq_number: int = Field(
        ..., ge=1, le=65535, description="Sequence number for this route map entry.", examples=[10, 20]
    )
    operation: Literal["permit", "deny"] = Field(
        ..., description="Action to take: permit or deny.", examples=["permit"]
    )
    description: Optional[str] = Field(
        default=None, description="Optional description for this entry.", examples=["Permit internal routes"]
    )
    continue_seq: Optional[int] = Field(
        default=None, ge=1, le=65535, description="Sequence number to continue to if this entry matches.", examples=[20]
    )
    match: Optional[RouteMapMatch] = Field(
        default=None, description="Match criteria for this entry."
    )
    set: Optional[RouteMapSet] = Field(
        default=None, description="Set actions to apply if match criteria are met."
    )

    model_config = {"extra": "forbid"}


class RouteMapCreate(BaseModel):
    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,62}$", 
        description="Unique name for the route map.", examples=["RM_INBOUND_FILTER"]
    )
    entries: list[RouteMapEntry] = Field(
        ..., min_length=1, description="List of entries defining the route map rules."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "ALLOW-DEFAULT",
                    "entries": [
                        {
                            "seq_number": 10, 
                            "operation": "permit", 
                            "match": {"ipv4": {"address_prefix_list": ["DEFAULT-ONLY"]}}
                        },
                    ],
                }
            ]
        }
    }


class RouteMapUpdate(BaseModel):
    entries: Optional[list[RouteMapEntry]] = Field(
        default=None, min_length=1, description="Updated list of route map entries."
    )

    model_config = {"extra": "forbid"}


class RouteMapRead(TimestampMixin):
    fabric_id: UUID = Field(description="UUID of the parent fabric.")
    name: str = Field(description="Name of the route map.")
    entries: list[RouteMapEntry] = Field(default=[], description="List of route map entries.")

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }