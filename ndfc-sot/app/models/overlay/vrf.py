"""VRF Pydantic models (E.18)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.common import TimestampMixin, validate_vlan_id, validate_vni


# ── VRF Switch Attachment ────────────────────────────────────────

class VrfSwitchAttachCreate(BaseModel):
    """Attach a VRF to a switch."""

    hostname: str = Field(..., max_length=128, description="Switch hostname (e.g., LEAF-1).", example="LEAF-1")
    vrf_lite: Optional[list[dict]] = Field(default=None, description="VRF Lite extension configuration.", example=[{"peer_vrf": "INTERNET", "interface": "Ethernet1/1"}])
    freeform_config: Optional[str] = Field(default=None, description="Per-switch freeform CLI configuration.", example="route-map RM_REDIST_STATIC permit 10")

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "hostname": "LEAF-1",
                    "vrf_lite": [{"peer_vrf": "INTERNET", "interface": "Ethernet1/1"}],
                    "freeform_config": "route-map RM_REDIST_STATIC permit 10"
                },
            ]
        }
    }


class VrfSwitchAttachRead(BaseModel):
    """Response body for a VRF switch attachment."""

    id: UUID = Field(description="Attachment UUID.")
    vrf_id: UUID = Field(description="Parent VRF UUID.")
    hostname: str = Field(description="Switch hostname.")
    vrf_lite: Optional[list[dict]] = Field(default=None, description="VRF Lite config.")
    freeform_config: Optional[str] = Field(default=None, description="Per-switch CLI.")

    model_config = {"from_attributes": True}


# ── VRF ──────────────────────────────────────────────────────────

class VrfCreate(BaseModel):
    """Request body to create a VRF."""

    fabric_id: UUID = Field(..., description="Parent fabric UUID.", example="00000000-0000-0000-0000-000000000001")
    name: str = Field(
        ...,
        min_length=1,
        max_length=32,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="VRF name.",
        example="VRF_PROD"
    )
    vrf_id: int = Field(..., description="VNI for the VRF.", example=50000)
    vlan_id: int = Field(..., description="VLAN ID for VRF SVI.", example=2000)
    vrf_description: Optional[str] = Field(default=None, max_length=256, description="VRF description.", example="Production VRF")
    route_target_both: Optional[bool] = Field(default=False, description="Auto route-target both.", example=True)
    route_target_import: Optional[str] = Field(default=None, description="Route-target import.", example="100:1")
    route_target_export: Optional[str] = Field(default=None, description="Route-target export.", example="100:1")
    route_target_import_evpn: Optional[str] = Field(default=None, description="EVPN route-target import.")
    route_target_export_evpn: Optional[str] = Field(default=None, description="EVPN route-target export.")
    ipv6_link_local_flag: Optional[bool] = Field(default=True, description="Enable IPv6 link-local.", example=True)
    max_bgp_paths: Optional[int] = Field(default=1, ge=1, le=64, description="Max BGP paths.", example=4)
    max_ibgp_paths: Optional[int] = Field(default=2, ge=1, le=64, description="Max iBGP paths.", example=4)
    advertise_host_routes: Optional[bool] = Field(default=False, description="Advertise host routes.", example=False)
    advertise_default_route: Optional[bool] = Field(default=True, description="Advertise default route.", example=True)
    enable_trm: Optional[bool] = Field(default=False, description="Enable TRM.", example=False)
    rp_address: Optional[str] = Field(default=None, description="RP address for TRM.", example="1.1.1.1")
    rp_external: Optional[bool] = Field(default=False, description="RP is external.", example=False)
    underlay_mcast_ip: Optional[str] = Field(default=None, description="Underlay multicast IP.", example="239.1.1.1")
    overlay_mcast_group: Optional[str] = Field(default=None, description="Overlay multicast group.", example="239.1.1.2")
    netflow_enable: Optional[bool] = Field(default=False, description="Enable NetFlow.", example=False)
    no_rp: Optional[bool] = Field(default=False, description="No RP flag.", example=False)
    route_map_in: Optional[str] = Field(default=None, description="Inbound route-map.", example="RM_IN")
    route_map_out: Optional[str] = Field(default=None, description="Outbound route-map.", example="RM_OUT")
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI config.", example="description Configured via SOT")
    switches: Optional[list[VrfSwitchAttachCreate]] = Field(default=None, description="Switch attachments.")

    @field_validator("vrf_id")
    @classmethod
    def _validate_vni(cls, v: int) -> int:
        return validate_vni(v)

    @field_validator("vlan_id")
    @classmethod
    def _validate_vlan(cls, v: int) -> int:
        return validate_vlan_id(v)

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "00000000-0000-0000-0000-000000000001",
                    "name": "VRF_PROD",
                    "vrf_id": 50000,
                    "vlan_id": 2000,
                    "advertise_default_route": True,
                    "switches": [{"hostname": "LEAF-1"}, {"hostname": "LEAF-2"}],
                }
            ]
        }
    }


class VrfUpdate(BaseModel):
    """Partial update for a VRF."""

    vrf_id: Optional[int] = Field(default=None, description="VRF VNI.", example=50000)
    vlan_id: Optional[int] = Field(default=None, description="VRF VLAN.", example=2000)
    vrf_description: Optional[str] = Field(default=None, max_length=256, description="Description.", example="Updated Production VRF")
    route_target_both: Optional[bool] = Field(default=None, description="RT both.", example=True)
    route_target_import: Optional[str] = Field(default=None, description="RT import.")
    route_target_export: Optional[str] = Field(default=None, description="RT export.")
    route_target_import_evpn: Optional[str] = Field(default=None, description="EVPN RT import.")
    route_target_export_evpn: Optional[str] = Field(default=None, description="EVPN RT export.")
    ipv6_link_local_flag: Optional[bool] = Field(default=None, description="IPv6 link-local.")
    max_bgp_paths: Optional[int] = Field(default=None, ge=1, le=64, description="Max BGP paths.")
    max_ibgp_paths: Optional[int] = Field(default=None, ge=1, le=64, description="Max iBGP paths.")
    advertise_host_routes: Optional[bool] = Field(default=None, description="Advertise host routes.")
    advertise_default_route: Optional[bool] = Field(default=None, description="Advertise default route.")
    enable_trm: Optional[bool] = Field(default=None, description="TRM enable.")
    rp_address: Optional[str] = Field(default=None, description="RP address.")
    rp_external: Optional[bool] = Field(default=None, description="RP external.")
    underlay_mcast_ip: Optional[str] = Field(default=None, description="Underlay multicast IP.")
    overlay_mcast_group: Optional[str] = Field(default=None, description="Overlay multicast group.")
    netflow_enable: Optional[bool] = Field(default=None, description="NetFlow.")
    no_rp: Optional[bool] = Field(default=None, description="No RP.")
    route_map_in: Optional[str] = Field(default=None, description="Route-map in.")
    route_map_out: Optional[str] = Field(default=None, description="Route-map out.")
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI.", example="description Updated via SOT")

    @field_validator("vrf_id")
    @classmethod
    def _validate_vni(cls, v: int | None) -> int | None:
        return validate_vni(v) if v is not None else v

    @field_validator("vlan_id")
    @classmethod
    def _validate_vlan(cls, v: int | None) -> int | None:
        return validate_vlan_id(v) if v is not None else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "vrf_description": "Updated Production VRF",
                    "advertise_default_route": True
                }
            ]
        }
    }


class VrfRead(TimestampMixin):
    """Response body for a VRF."""

    fabric_id: UUID = Field(description="Parent fabric UUID.")
    name: str = Field(description="VRF name.")
    vrf_id: int = Field(description="VRF VNI.")
    vlan_id: int = Field(description="VRF VLAN.")
    vrf_description: Optional[str] = Field(default=None, description="Description.")
    route_target_both: Optional[bool] = Field(default=None, description="RT both.")
    route_target_import: Optional[str] = Field(default=None, description="RT import.")
    route_target_export: Optional[str] = Field(default=None, description="RT export.")
    route_target_import_evpn: Optional[str] = Field(default=None, description="EVPN RT import.")
    route_target_export_evpn: Optional[str] = Field(default=None, description="EVPN RT export.")
    ipv6_link_local_flag: Optional[bool] = Field(default=None, description="IPv6 link-local.")
    max_bgp_paths: Optional[int] = Field(default=None, description="Max BGP paths.")
    max_ibgp_paths: Optional[int] = Field(default=None, description="Max iBGP paths.")
    advertise_host_routes: Optional[bool] = Field(default=None, description="Advertise host routes.")
    advertise_default_route: Optional[bool] = Field(default=None, description="Advertise default route.")
    enable_trm: Optional[bool] = Field(default=None, description="TRM.")
    rp_address: Optional[str] = Field(default=None, description="RP address.")
    rp_external: Optional[bool] = Field(default=None, description="RP external.")
    underlay_mcast_ip: Optional[str] = Field(default=None, description="Underlay multicast IP.")
    overlay_mcast_group: Optional[str] = Field(default=None, description="Overlay multicast group.")
    netflow_enable: Optional[bool] = Field(default=None, description="NetFlow.")
    no_rp: Optional[bool] = Field(default=None, description="No RP.")
    route_map_in: Optional[str] = Field(default=None, description="Route-map in.")
    route_map_out: Optional[str] = Field(default=None, description="Route-map out.")
    freeform_config: Optional[str] = Field(default=None, description="Freeform CLI.")

    model_config = {"from_attributes": True}
