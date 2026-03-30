"""Interface discriminated union and shared read/update models."""

from __future__ import annotations

from typing import Annotated, Literal, Optional, Union
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Discriminator, Field, Tag, model_validator

from app.models.interfaces.access import AccessInterfaceCreate
from app.models.interfaces.access_port_channel import AccessPortChannelCreate
from app.models.interfaces.trunk import TrunkInterfaceCreate
from app.models.interfaces.trunk_port_channel import TrunkPortChannelCreate
from app.models.interfaces.loopback import LoopbackInterfaceCreate, SecondaryIpv4
from app.models.interfaces.routed import RoutedInterfaceCreate
from app.models.interfaces.routed_port_channel import RoutedPortChannelCreate
from app.models.interfaces.routed_sub import RoutedSubInterfaceCreate
from app.models.interfaces.breakout import BreakoutInterfaceCreate
from app.models.interfaces.dot1q_tunnel import Dot1qTunnelInterfaceCreate


def _interface_discriminator(v: dict | BaseModel) -> str:
    """Custom discriminator that maps fabric_loopback -> loopback model."""
    mode = v.get("mode") if isinstance(v, dict) else getattr(v, "mode", None)
    if mode == "fabric_loopback":
        return "loopback"
    return mode  # type: ignore[return-value]


InterfaceCreate = Annotated[
    Union[
        Annotated[AccessInterfaceCreate, Tag("access")],
        Annotated[AccessPortChannelCreate, Tag("access_port_channel")],
        Annotated[TrunkInterfaceCreate, Tag("trunk")],
        Annotated[TrunkPortChannelCreate, Tag("trunk_port_channel")],
        Annotated[LoopbackInterfaceCreate, Tag("loopback")],
        Annotated[RoutedInterfaceCreate, Tag("routed")],
        Annotated[RoutedPortChannelCreate, Tag("routed_port_channel")],
        Annotated[RoutedSubInterfaceCreate, Tag("routed_sub")],
        Annotated[BreakoutInterfaceCreate, Tag("breakout")],
        Annotated[Dot1qTunnelInterfaceCreate, Tag("dot1q_tunnel")],
    ],
    Discriminator(_interface_discriminator),
]


class InterfaceUpdate(BaseModel):
    """Update an existing interface. All fields optional; mode cannot change."""

    description: Optional[str] = Field(default=None, max_length=256, description="Interface description.", example="Configured via SOT")
    enabled: Optional[bool] = Field(default=None, description="Administrative state.", example=True)
    freeform_config: Optional[str] = Field(default=None, description="Per-interface freeform CLI configuration.", example="description Configured via SOT")
    access_vlan: Optional[int] = Field(default=None, ge=1, le=4094, description="Access VLAN ID.", example=10)
    native_vlan: Optional[int] = Field(default=None, ge=1, le=4094, description="Native VLAN ID.", example=1)
    trunk_allowed_vlans: Optional[str] = Field(default=None, description="Allowed VLAN ranges as string.", example="10,20,100-200")
    mtu: Optional[Union[str, int]] = Field(default=None, description="Maximum Transmission Unit (MTU).", example="9216")
    speed: Optional[str] = Field(default=None, description="Interface speed.", example="10gb")
    duplex: Optional[Literal["auto", "full", "half"]] = Field(default=None, description="Interface duplex mode.", example="full")
    vpc_id: Optional[int] = Field(default=None, ge=1, le=4096, description="Virtual Port-Channel (vPC) ID.", example=10)
    pc_mode: Optional[Literal["active", "passive", "on"]] = Field(default=None, description="Port-channel LACP mode.", example="active")
    members: Optional[list[str]] = Field(default=None, description="Member physical interfaces for a port-channel.", example=["Ethernet1/1", "Ethernet1/2"])
    vrf: Optional[str] = Field(default=None, description="VRF name for L3 interfaces.", example="VRF_PROD")
    ipv4_address: Optional[str] = Field(default=None, description="IPv4 address with CIDR mask.", example="192.168.1.1/24")
    ipv6_address: Optional[str] = Field(default=None, description="IPv6 address with CIDR mask.", example="2001:db8::1/64")
    ipv4_route_tag: Optional[int] = Field(default=None, description="IPv4 routing tag.", example=12345)
    secondary_ipv4: Optional[list[SecondaryIpv4]] = Field(default=None, description="Secondary IPv4 addresses.")
    dot1q_id: Optional[int] = Field(default=None, ge=1, le=4096, description="802.1Q sub-interface ID.", example=100)
    spanning_tree_portfast: Optional[bool] = Field(default=None, description="Enable Spanning-Tree Portfast.", example=True)
    ospf_area: Optional[str] = Field(default=None, description="OSPF area ID.", example="0.0.0.0")
    ospf_auth_enable: Optional[bool] = Field(default=None, description="Enable OSPF authentication.", example=False)
    ospf_auth_key: Optional[str] = Field(default=None, description="OSPF authentication key.", example="cisco123")
    route_map_tag: Optional[str] = Field(default=None, description="Route-map tag for redistribution.", example="RM_REDIST")
    breakout_mode: Optional[str] = Field(default=None, description="Interface breakout mode.", example="4x10g")
    tunnel_vlan: Optional[int] = Field(default=None, ge=1, le=4094, description="Dot1Q tunnel VLAN ID.", example=2000)

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "description": "Updated via SOT",
                    "enabled": True,
                    "access_vlan": 10
                }
            ]
        }
    }


class InterfaceRead(BaseModel):
    """Response body for an interface (all possible fields)."""

    id: UUID
    switch_id: UUID
    name: str = Field(description="Interface name.")
    mode: str = Field(alias="type", description="Interface mode/type.")
    description: Optional[str] = None
    enabled: Optional[bool] = Field(alias="admin_state", default=None)
    freeform_config: Optional[str] = None
    access_vlan: Optional[int] = None
    native_vlan: Optional[int] = None
    trunk_allowed_vlans: Optional[str] = None
    mtu: Optional[Union[str, int]] = None
    speed: Optional[str] = None
    duplex: Optional[str] = None
    vpc_id: Optional[int] = None
    pc_mode: Optional[str] = None
    members: Optional[list[str]] = None
    vrf: Optional[str] = None
    ipv4_address: Optional[str] = None
    ipv6_address: Optional[str] = None
    ipv4_route_tag: Optional[int] = None
    secondary_ipv4: Optional[list[SecondaryIpv4]] = None
    dot1q_id: Optional[int] = None
    spanning_tree_portfast: Optional[bool] = None
    ospf_area: Optional[str] = None
    ospf_auth_enable: Optional[bool] = None
    ospf_auth_key: Optional[str] = None
    route_map_tag: Optional[str] = None
    breakout_mode: Optional[str] = None
    tunnel_vlan: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _flatten_type_config(cls, data: any) -> any:
        """Flatten type_config into top-level fields for ORM objects."""
        if hasattr(data, "type_config") and isinstance(data.type_config, dict):
            # If it's an ORM object, we create a dict to merge fields
            # This allows Pydantic to find 'access_vlan' etc. from the JSONB column
            res = {**data.__dict__}
            res.update(data.type_config)
            # Ensure aliases work for ORM objects by providing the expected names
            res["mode"] = data.type
            res["enabled"] = data.admin_state
            return res
        return data

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


__all__ = [
    "InterfaceCreate",
    "InterfaceUpdate",
    "InterfaceRead",
    "AccessInterfaceCreate",
    "AccessPortChannelCreate",
    "TrunkInterfaceCreate",
    "TrunkPortChannelCreate",
    "LoopbackInterfaceCreate",
    "RoutedInterfaceCreate",
    "RoutedPortChannelCreate",
    "RoutedSubInterfaceCreate",
    "BreakoutInterfaceCreate",
    "Dot1qTunnelInterfaceCreate",
    "SecondaryIpv4",
]
