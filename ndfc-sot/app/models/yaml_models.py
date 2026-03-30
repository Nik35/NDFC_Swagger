"""YAML-oriented output models matching NAC-DC YAML keys exactly.

These are used by the YAML builder to serialize fabric data into the
correct NAC-DC structure without extra DB metadata fields.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class _YamlBase(BaseModel):
    """All YAML models exclude None values during serialization."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        # When calling .model_dump(exclude_none=True) the caller controls
        # whether None fields are emitted.
    )


class YamlManagement(_YamlBase):
    management_ipv4_address: Optional[str] = Field(
        default=None,
        description="Management IPv4 address.",
        examples=["192.168.1.10"]
    )
    management_ipv6_address: Optional[str] = Field(
        default=None,
        description="Management IPv6 address.",
        examples=["2001:db8:m::10"]
    )
    default_gateway_v4: Optional[str] = Field(
        default=None,
        description="IPv4 default gateway.",
        examples=["192.168.1.1"]
    )
    default_gateway_v6: Optional[str] = Field(
        default=None,
        description="IPv6 default gateway.",
        examples=["2001:db8:m::1"]
    )
    subnet_mask_ipv4: Optional[int] = Field(
        default=None,
        ge=0,
        le=32,
        description="IPv4 subnet mask prefix length.",
        examples=[24]
    )
    subnet_mask_ipv6: Optional[int] = Field(
        default=None,
        ge=0,
        le=128,
        description="IPv6 subnet mask prefix length.",
        examples=[64]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "management_ipv4_address": "192.168.1.10",
                    "default_gateway_v4": "192.168.1.1",
                    "subnet_mask_ipv4": 24,
                }
            ]
        }
    )


class YamlPoap(_YamlBase):
    bootstrap: Optional[bool] = Field(
        default=None,
        description="Enable POAP bootstrap.",
        examples=[True]
    )
    discovery_creds: Optional[bool] = Field(
        default=None,
        description="Use discovery credentials.",
        examples=[True]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "bootstrap": True,
                    "discovery_creds": False,
                }
            ]
        }
    )


class YamlInterface(_YamlBase):
    name: str = Field(
        ...,
        description="Interface name (e.g., Ethernet1/1).",
        examples=["Ethernet1/1"]
    )
    mode: str = Field(
        ...,
        description="Interface mode (access, trunk, routed, etc.).",
        examples=["trunk"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Interface description.",
        examples=["Link to SPINE-1"]
    )
    enabled: Optional[bool] = Field(
        default=None,
        description="Administrative state.",
        examples=[True]
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI configuration.",
        examples=["speed 10000"]
    )
    access_vlan: Optional[int] = Field(
        default=None,
        ge=1,
        le=4094,
        description="Access VLAN ID.",
        examples=[10]
    )
    native_vlan: Optional[int] = Field(
        default=None,
        ge=1,
        le=4094,
        description="Native VLAN ID.",
        examples=[1]
    )
    trunk_allowed_vlans: Optional[list[dict]] = Field(
        default=None,
        description="List of allowed VLANs.",
        examples=[[{"vlan_id": 10}, {"vlan_id": 20}]]
    )
    mtu: Optional[str] = Field(
        default=None,
        description="Interface MTU.",
        examples=["9216"]
    )
    speed: Optional[str] = Field(
        default=None,
        description="Interface speed.",
        examples=["10G"]
    )
    duplex: Optional[str] = Field(
        default=None,
        description="Interface duplex.",
        examples=["full"]
    )
    vpc_id: Optional[int] = Field(
        default=None,
        description="vPC ID.",
        examples=[1]
    )
    pc_mode: Optional[str] = Field(
        default=None,
        description="Port-channel mode (active, passive, on).",
        examples=["active"]
    )
    members: Optional[list[str]] = Field(
        default=None,
        description="Member interfaces for port-channels.",
        examples=[["Ethernet1/1", "Ethernet1/2"]]
    )
    vrf: Optional[str] = Field(
        default=None,
        description="VRF name.",
        examples=["tenant-1"]
    )
    ipv4_address: Optional[str] = Field(
        default=None,
        description="IPv4 address with CIDR.",
        examples=["10.1.1.1/24"]
    )
    ipv6_address: Optional[str] = Field(
        default=None,
        description="IPv6 address with CIDR.",
        examples=["2001:db8:1::1/64"]
    )
    ipv4_route_tag: Optional[int] = Field(
        default=None,
        description="Route tag for IPv4.",
        examples=[12345]
    )
    secondary_ipv4: Optional[list[dict]] = Field(
        default=None,
        description="List of secondary IPv4 addresses.",
        examples=[[{"ipv4_address": "10.1.1.2/24"}]]
    )
    dot1q_id: Optional[int] = Field(
        default=None,
        description="802.1Q tag ID.",
        examples=[100]
    )
    spanning_tree_portfast: Optional[bool] = Field(
        default=None,
        description="Enable Spanning Tree PortFast.",
        examples=[True]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Ethernet1/1",
                    "mode": "trunk",
                    "trunk_allowed_vlans": [{"vlan_id": 10}, {"vlan_id": 20}],
                    "spanning_tree_portfast": True,
                }
            ]
        }
    )


class YamlSwitch(_YamlBase):
    name: str = Field(
        ...,
        description="Switch hostname.",
        examples=["LEAF-1"]
    )
    serial_number: Optional[str] = Field(
        default=None,
        description="Switch serial number.",
        examples=["SAL12345678"]
    )
    role: Optional[str] = Field(
        default=None,
        description="Switch role in fabric.",
        examples=["leaf"]
    )
    routing_loopback_id: Optional[int] = Field(
        default=None,
        description="Routing loopback ID.",
        examples=[0]
    )
    vtep_loopback_id: Optional[int] = Field(
        default=None,
        description="VTEP loopback ID.",
        examples=[1]
    )
    management: Optional[YamlManagement] = Field(
        default=None,
        description="Management interface configuration."
    )
    poap: Optional[YamlPoap] = Field(
        default=None,
        description="POAP configuration."
    )
    interfaces: Optional[list[YamlInterface]] = Field(
        default=None,
        description="List of interface configurations."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "LEAF-1",
                    "role": "leaf",
                    "management": {
                        "management_ipv4_address": "192.168.1.10",
                        "subnet_mask_ipv4": 24,
                    },
                    "interfaces": [
                        {"name": "Ethernet1/1", "mode": "access", "access_vlan": 10}
                    ],
                }
            ]
        }
    )


class YamlVpcPeer(_YamlBase):
    peer1: str = Field(
        ...,
        description="Hostname of the first peer.",
        examples=["LEAF-1"]
    )
    peer2: str = Field(
        ...,
        description="Hostname of the second peer.",
        examples=["LEAF-2"]
    )
    fabric_peering: Optional[bool] = Field(
        default=None,
        description="Enable fabric peering.",
        examples=[True]
    )
    domain_id: Optional[int] = Field(
        default=None,
        description="vPC domain ID.",
        examples=[10]
    )
    peer1_peerlink_interfaces: Optional[list[str]] = Field(
        default=None,
        description="Peer 1 peer-link interfaces.",
        examples=[["Ethernet1/49", "Ethernet1/50"]]
    )
    peer2_peerlink_interfaces: Optional[list[str]] = Field(
        default=None,
        description="Peer 2 peer-link interfaces.",
        examples=[["Ethernet1/49", "Ethernet1/50"]]
    )
    vtep_vip: Optional[str] = Field(
        default=None,
        description="Anycast VTEP VIP.",
        examples=["10.255.255.1"]
    )
    keepalive_vrf: Optional[str] = Field(
        default=None,
        description="VRF for peer keepalive.",
        examples=["management"]
    )
    peer1_keepalive_ipv4: Optional[str] = Field(
        default=None,
        description="Peer 1 keepalive IPv4.",
        examples=["192.168.100.1"]
    )
    peer2_keepalive_ipv4: Optional[str] = Field(
        default=None,
        description="Peer 2 keepalive IPv4.",
        examples=["192.168.100.2"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "peer1": "LEAF-1",
                    "peer2": "LEAF-2",
                    "domain_id": 10,
                    "peer1_peerlink_interfaces": ["Ethernet1/49", "Ethernet1/50"],
                    "peer2_peerlink_interfaces": ["Ethernet1/49", "Ethernet1/50"],
                }
            ]
        }
    )


class YamlVrf(_YamlBase):
    name: str = Field(
        ...,
        description="VRF name.",
        examples=["tenant-1"]
    )
    vrf_id: Optional[int] = Field(
        default=None,
        description="VRF VNID / Segment ID.",
        examples=[50001]
    )
    vlan_id: Optional[int] = Field(
        default=None,
        description="VRF VLAN ID.",
        examples=[2000]
    )
    vrf_attach_group: Optional[str] = Field(
        default=None,
        description="Switch group to attach this VRF.",
        examples=["all-leafs"]
    )
    vrf_int_mtu: Optional[int] = Field(
        default=None,
        description="VRF interface MTU.",
        examples=[9216]
    )
    trm_enable: Optional[bool] = Field(
        default=None,
        description="Enable Tenant Routed Multicast.",
        examples=[False]
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI configuration.",
        examples=["ip route 0.0.0.0/0 10.1.1.254"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "VRF-A",
                    "vrf_id": 50001,
                    "vlan_id": 2000,
                }
            ]
        }
    )


class YamlNetwork(_YamlBase):
    name: str = Field(
        ...,
        description="Network name.",
        examples=["vlan10-net"]
    )
    vrf_name: Optional[str] = Field(
        default=None,
        description="Parent VRF name.",
        examples=["tenant-1"]
    )
    is_l2_only: Optional[bool] = Field(
        default=None,
        description="Is this an L2-only network.",
        examples=[False]
    )
    attach_group_name: Optional[str] = Field(
        default=None,
        description="Switch group to attach this network.",
        examples=["all-leafs"]
    )
    net_id: Optional[int] = Field(
        default=None,
        description="Network VNID / Segment ID.",
        examples=[30010]
    )
    vlan_id: Optional[int] = Field(
        default=None,
        description="Network VLAN ID.",
        examples=[10]
    )
    gw_ip_address: Optional[str] = Field(
        default=None,
        description="Anycast gateway IPv4 address with CIDR.",
        examples=["10.1.10.1/24"]
    )
    gw_ipv6_address: Optional[str] = Field(
        default=None,
        description="Anycast gateway IPv6 address with CIDR.",
        examples=["2001:db8:10::1/64"]
    )
    dhcp_servers: Optional[list[dict]] = Field(
        default=None,
        description="List of DHCP relay servers.",
        examples=[[{"server_ip": "10.1.1.100"}]]
    )
    freeform_config: Optional[str] = Field(
        default=None,
        description="Freeform CLI configuration.",
        examples=["no redirect"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "NET-10",
                    "vrf_name": "VRF-A",
                    "vlan_id": 10,
                    "gw_ip_address": "10.1.10.1/24",
                }
            ]
        }
    )


class YamlFabricRoot(_YamlBase):
    """Top-level structure matching NAC-DC YAML."""

    vxlan: dict[str, Any] = Field(
        ...,
        description="VXLAN fabric configuration container.",
        examples=[{"fabrics": {"FABRIC-1": {"switches": []}}}]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "vxlan": {
                        "fabrics": {
                            "DC-FABRIC-1": {
                                "switches": [
                                    {"name": "LEAF-1", "role": "leaf"}
                                ]
                            }
                        }
                    }
                }
            ]
        }
    )