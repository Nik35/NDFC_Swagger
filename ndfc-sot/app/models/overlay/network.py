"""Network Pydantic models (E.19)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.common import (
    TimestampMixin,
    validate_cidr,
    validate_ipv4,
    validate_multicast_v4,
    validate_vlan_id,
    validate_vni,
)


# ── Network Switch Attachment ────────────────────────────────────

class NetworkSwitchAttachCreate(BaseModel):
    """Attach a network to a switch."""

    hostname: str = Field(..., max_length=128, description="Switch hostname (e.g., LEAF-1).", example="LEAF-1")
    ports: Optional[list[str]] = Field(default=None, description="Attached switch ports (e.g., ['Ethernet1/10']).", example=["Ethernet1/10"])
    freeform_config: Optional[str] = Field(default=None, description="Per-switch freeform CLI configuration.", example="interface nve1\n  member vni 30001 mcast-group 239.1.1.1")

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "hostname": "LEAF-1",
                    "ports": ["Ethernet1/10"],
                    "freeform_config": "interface nve1\n  member vni 30001 mcast-group 239.1.1.1"
                },
            ]
        }
    }


class NetworkSwitchAttachRead(BaseModel):
    """Response body for a network switch attachment."""

    id: UUID = Field(description="Attachment UUID.")
    network_id: UUID = Field(description="Parent network UUID.")
    hostname: str = Field(description="Switch hostname.")
    ports: Optional[list[str]] = Field(default=None, description="Attached ports.")
    freeform_config: Optional[str] = Field(default=None, description="Per-switch CLI.")

    model_config = {"from_attributes": True}


# ── Network ──────────────────────────────────────────────────────

class NetworkCreate(BaseModel):
    """Request body to create a network."""

    fabric_id: UUID = Field(..., description="Parent fabric UUID.", example="00000000-0000-0000-0000-000000000001")
    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Network name.",
        example="NET_WEB_100"
    )
    network_id: int = Field(..., description="L2 VNI (network segment ID).", example=30001)
    vlan_id: int = Field(..., description="VLAN ID.", example=100)
    vlan_name: Optional[str] = Field(default=None, max_length=128, description="VLAN name.", example="VLAN_WEB_100")
    vrf_name: Optional[str] = Field(default=None, description="VRF name (required for L3).", example="VRF_PROD")
    gateway_ipv4: Optional[str] = Field(default=None, description="Anycast gateway IPv4 CIDR.", example="10.1.100.1/24")
    gateway_ipv6: Optional[str] = Field(default=None, description="Anycast gateway IPv6 CIDR.", example="2001:db8:100::1/64")
    suppress_arp: Optional[bool] = Field(default=False, description="Enable ARP suppression.", example=True)
    enable_ir: Optional[bool] = Field(default=False, description="Enable ingress replication.", example=False)
    mtu: Optional[int] = Field(default=9216, ge=68, le=9216, description="L3 interface MTU.", example=9216)
    routing_tag: Optional[int] = Field(default=12345, ge=0, le=4294967295, description="Routing tag.", example=12345)
    is_l2_only: Optional[bool] = Field(default=False, description="L2-only network (no gateway).", example=False)
    multicast_group: Optional[str] = Field(default=None, description="Multicast group address.", example="239.1.1.1")
    dhcp_server_addr_1: Optional[str] = Field(default=None, description="DHCP server address 1.", example="10.1.1.10")
    dhcp_server_addr_2: Optional[str] = Field(default=None, description="DHCP server address 2.", example="10.1.1.11")
    dhcp_server_addr_3: Optional[str] = Field(default=None, description="DHCP server address 3.")
    dhcp_server_vrf: Optional[str] = Field(default=None, description="DHCP server VRF.", example="VRF_MGMT")
    loopback_id: Optional[int] = Field(default=None, ge=0, le=1023, description="DHCP loopback ID.", example=0)
    enable_trm: Optional[bool] = Field(default=False, description="Enable TRM.", example=False)
    route_map_in: Optional[str] = Field(default=None, description="Inbound route-map.", example="RM_IN")
    netflow_enable: Optional[bool] = Field(default=False, description="Enable NetFlow.", example=False)
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI config.", example="description Configured via SOT")
    switches: Optional[list[NetworkSwitchAttachCreate]] = Field(default=None, description="Switch attachments.")

    @model_validator(mode="after")
    def _l3_requires_vrf(self) -> "NetworkCreate":
        if not self.is_l2_only and not self.vrf_name:
            raise ValueError("vrf_name is required for L3 networks (is_l2_only=False)")
        return self

    @field_validator("gateway_ipv4", "gateway_ipv6")
    @classmethod
    def _validate_gw(cls, v: str | None) -> str | None:
        return validate_cidr(v) if v else v

    @field_validator("multicast_group")
    @classmethod
    def _validate_mcast(cls, v: str | None) -> str | None:
        return validate_multicast_v4(v) if v else v

    @field_validator("network_id")
    @classmethod
    def _validate_vni(cls, v: int) -> int:
        return validate_vni(v)

    @field_validator("vlan_id")
    @classmethod
    def _validate_vlan(cls, v: int) -> int:
        return validate_vlan_id(v)

    @field_validator("dhcp_server_addr_1", "dhcp_server_addr_2", "dhcp_server_addr_3")
    @classmethod
    def _validate_dhcp(cls, v: str | None) -> str | None:
        return validate_ipv4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "00000000-0000-0000-0000-000000000001",
                    "name": "NET_WEB_100",
                    "network_id": 30001,
                    "vlan_id": 100,
                    "vrf_name": "VRF_PROD",
                    "gateway_ipv4": "10.1.100.1/24",
                    "suppress_arp": True,
                    "switches": [{"hostname": "LEAF-1", "ports": ["Ethernet1/10"]}],
                }
            ]
        }
    }


class NetworkUpdate(BaseModel):
    """Partial update for a network."""

    vlan_name: Optional[str] = Field(default=None, max_length=128, description="VLAN name.", example="VLAN_WEB_100_UPDATED")
    vrf_name: Optional[str] = Field(default=None, description="VRF name.", example="VRF_PROD")
    gateway_ipv4: Optional[str] = Field(default=None, description="Gateway IPv4.", example="10.1.100.1/24")
    gateway_ipv6: Optional[str] = Field(default=None, description="Gateway IPv6.", example="2001:db8:100::1/64")
    suppress_arp: Optional[bool] = Field(default=None, description="ARP suppression.", example=True)
    enable_ir: Optional[bool] = Field(default=None, description="Ingress replication.", example=False)
    mtu: Optional[int] = Field(default=None, ge=68, le=9216, description="MTU.", example=9216)
    routing_tag: Optional[int] = Field(default=None, ge=0, le=4294967295, description="Routing tag.", example=12345)
    is_l2_only: Optional[bool] = Field(default=None, description="L2-only.", example=False)
    multicast_group: Optional[str] = Field(default=None, description="Multicast group.", example="239.1.1.1")
    dhcp_server_addr_1: Optional[str] = Field(default=None, description="DHCP server 1.", example="10.1.1.10")
    dhcp_server_addr_2: Optional[str] = Field(default=None, description="DHCP server 2.", example="10.1.1.11")
    dhcp_server_addr_3: Optional[str] = Field(default=None, description="DHCP server 3.")
    dhcp_server_vrf: Optional[str] = Field(default=None, description="DHCP VRF.", example="VRF_MGMT")
    loopback_id: Optional[int] = Field(default=None, ge=0, le=1023, description="DHCP loopback.", example=0)
    enable_trm: Optional[bool] = Field(default=None, description="TRM enable.", example=False)
    route_map_in: Optional[str] = Field(default=None, description="Route-map in.", example="RM_IN")
    netflow_enable: Optional[bool] = Field(default=None, description="NetFlow.", example=False)
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI.", example="description Updated via SOT")

    @field_validator("gateway_ipv4", "gateway_ipv6")
    @classmethod
    def _validate_gw(cls, v: str | None) -> str | None:
        return validate_cidr(v) if v else v

    @field_validator("multicast_group")
    @classmethod
    def _validate_mcast(cls, v: str | None) -> str | None:
        return validate_multicast_v4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "vlan_name": "VLAN_WEB_100_UPDATED",
                    "gateway_ipv4": "10.1.100.1/24",
                    "suppress_arp": True
                }
            ]
        }
    }


class NetworkRead(TimestampMixin):
    """Response body for a network."""

    fabric_id: UUID = Field(description="Parent fabric UUID.")
    name: str = Field(description="Network name.")
    network_id: int = Field(description="L2 VNI.")
    vlan_id: int = Field(description="VLAN ID.")
    vlan_name: Optional[str] = Field(default=None, description="VLAN name.")
    vrf_name: Optional[str] = Field(default=None, description="VRF name.")
    gateway_ipv4: Optional[str] = Field(default=None, description="Gateway IPv4.")
    gateway_ipv6: Optional[str] = Field(default=None, description="Gateway IPv6.")
    suppress_arp: Optional[bool] = Field(default=None, description="ARP suppression.")
    enable_ir: Optional[bool] = Field(default=None, description="Ingress replication.")
    mtu: Optional[int] = Field(default=None, description="MTU.")
    routing_tag: Optional[int] = Field(default=None, description="Routing tag.")
    is_l2_only: Optional[bool] = Field(default=None, description="L2-only.")
    multicast_group: Optional[str] = Field(default=None, description="Multicast group.")
    dhcp_server_addr_1: Optional[str] = Field(default=None, description="DHCP server 1.")
    dhcp_server_addr_2: Optional[str] = Field(default=None, description="DHCP server 2.")
    dhcp_server_addr_3: Optional[str] = Field(default=None, description="DHCP server 3.")
    dhcp_server_vrf: Optional[str] = Field(default=None, description="DHCP VRF.")
    loopback_id: Optional[int] = Field(default=None, description="DHCP loopback.")
    enable_trm: Optional[bool] = Field(default=None, description="TRM.")
    route_map_in: Optional[str] = Field(default=None, description="Route-map in.")
    netflow_enable: Optional[bool] = Field(default=None, description="NetFlow.")
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI.")

    model_config = {"from_attributes": True}
