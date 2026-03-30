"""Global configuration Pydantic models (E.2)."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.common import TimestampMixin, validate_bgp_asn, validate_ipv4, validate_mac


GLOBAL_TYPES = Literal["vxlan_evpn_ibgp", "vxlan_evpn_ebgp", "external"]


class GlobalConfigCreate(BaseModel):
    """Request body to create a global config (one per fabric)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    global_type: GLOBAL_TYPES = Field(
        default="vxlan_evpn_ibgp",
        description="Global sub-type discriminator.",
        examples=["vxlan_evpn_ibgp"]
    )
    bgp_asn: str = Field(
        ...,
        description="BGP ASN (plain or asdot).",
        examples=["65001"]
    )
    route_reflectors: Optional[int] = Field(
        default=2,
        ge=1,
        le=4,
        description="Number of route reflectors.",
        examples=[2]
    )
    anycast_gateway_mac: Optional[str] = Field(
        default=None,
        description="Anycast gateway MAC address.",
        examples=["0011.2233.4455"]
    )
    enable_nxapi_http: Optional[bool] = Field(
        default=False,
        description="Enable NX-API HTTP.",
        examples=[False]
    )
    enable_nxapi_https: Optional[bool] = Field(
        default=True,
        description="Enable NX-API HTTPS.",
        examples=[True]
    )
    enable_realtime_backup: Optional[bool] = Field(
        default=False,
        description="Enable real-time backup.",
        examples=[True]
    )
    enable_scheduled_backup: Optional[bool] = Field(
        default=False,
        description="Enable scheduled backup.",
        examples=[False]
    )
    inband_mgmt: Optional[bool] = Field(
        default=False,
        description="Enable in-band management.",
        examples=[False]
    )
    bootstrap_enable: Optional[bool] = Field(
        default=False,
        description="Enable POAP bootstrap.",
        examples=[True]
    )
    dhcp_enable: Optional[bool] = Field(
        default=False,
        description="Enable DHCP for bootstrap.",
        examples=[True]
    )
    dns_server_ip: Optional[str] = Field(
        default=None,
        description="DNS server IPv4 address.",
        examples=["8.8.8.8"]
    )
    dns_server_vrf: Optional[str] = Field(
        default="management",
        description="DNS server VRF.",
        examples=["management"]
    )
    ntp_server_ip: Optional[str] = Field(
        default=None,
        description="NTP server IPv4 address.",
        examples=["10.1.1.1"]
    )
    ntp_server_vrf: Optional[str] = Field(
        default="management",
        description="NTP server VRF.",
        examples=["management"]
    )
    syslog_server_ip: Optional[str] = Field(
        default=None,
        description="Syslog server IPv4 address.",
        examples=["10.1.1.2"]
    )
    syslog_server_vrf: Optional[str] = Field(
        default="management",
        description="Syslog server VRF.",
        examples=["management"]
    )
    syslog_severity: Optional[str] = Field(
        default="5",
        description="Syslog severity level.",
        examples=["6"]
    )
    aaa_server_conf: Optional[str] = Field(
        default=None,
        description="AAA server configuration.",
        examples=["radius-server host 10.1.1.3 key v3ry-53cr3t"]
    )
    extra_conf_leaf: Optional[str] = Field(
        default=None,
        description="Extra freeform config for leaf switches.",
        examples=["feature interface-vlan"]
    )
    extra_conf_spine: Optional[str] = Field(
        default=None,
        description="Extra freeform config for spine switches.",
        examples=["feature ospf"]
    )
    netflow_enable: Optional[bool] = Field(
        default=False,
        description="Enable NetFlow.",
        examples=[True]
    )
    extra_config: Optional[dict] = Field(
        default=None,
        description="JSONB extra config for non-standard global_type fields.",
        examples=[{"overlay_mtu": 9216}]
    )

    @field_validator("bgp_asn")
    @classmethod
    def _validate_bgp_asn(cls, v: str) -> str:
        return validate_bgp_asn(v)

    @field_validator("anycast_gateway_mac")
    @classmethod
    def _validate_mac(cls, v: str | None) -> str | None:
        return validate_mac(v) if v else v

    @field_validator("dns_server_ip", "ntp_server_ip", "syslog_server_ip")
    @classmethod
    def _validate_ip(cls, v: str | None) -> str | None:
        return validate_ipv4(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "global_type": "vxlan_evpn_ibgp",
                    "bgp_asn": "65000",
                    "route_reflectors": 2,
                    "anycast_gateway_mac": "0011.2233.4455",
                    "enable_nxapi_http": False,
                    "dns_server_ip": "10.1.1.100",
                    "ntp_server_ip": "10.1.1.101",
                }
            ]
        }
    }


class GlobalConfigUpdate(BaseModel):
    """Update global config. global_type cannot change."""

    bgp_asn: Optional[str] = Field(
        default=None,
        description="BGP ASN.",
        examples=["65002"]
    )
    route_reflectors: Optional[int] = Field(
        default=None,
        ge=1,
        le=4,
        description="Route reflectors.",
        examples=[4]
    )
    anycast_gateway_mac: Optional[str] = Field(
        default=None,
        description="Anycast GW MAC.",
        examples=["aaaa.bbbb.cccc"]
    )
    enable_nxapi_http: Optional[bool] = Field(
        default=None,
        description="NX-API HTTP.",
        examples=[True]
    )
    enable_nxapi_https: Optional[bool] = Field(
        default=None,
        description="NX-API HTTPS.",
        examples=[False]
    )
    enable_realtime_backup: Optional[bool] = Field(
        default=None,
        description="Realtime backup.",
        examples=[False]
    )
    enable_scheduled_backup: Optional[bool] = Field(
        default=None,
        description="Scheduled backup.",
        examples=[True]
    )
    inband_mgmt: Optional[bool] = Field(
        default=None,
        description="In-band management.",
        examples=[True]
    )
    bootstrap_enable: Optional[bool] = Field(
        default=None,
        description="POAP bootstrap.",
        examples=[False]
    )
    dhcp_enable: Optional[bool] = Field(
        default=None,
        description="DHCP enable.",
        examples=[False]
    )
    dns_server_ip: Optional[str] = Field(
        default=None,
        description="DNS server IP.",
        examples=["1.1.1.1"]
    )
    dns_server_vrf: Optional[str] = Field(
        default=None,
        description="DNS server VRF.",
        examples=["default"]
    )
    ntp_server_ip: Optional[str] = Field(
        default=None,
        description="NTP server IP.",
        examples=["2.2.2.2"]
    )
    ntp_server_vrf: Optional[str] = Field(
        default=None,
        description="NTP server VRF.",
        examples=["default"]
    )
    syslog_server_ip: Optional[str] = Field(
        default=None,
        description="Syslog server IP.",
        examples=["3.3.3.3"]
    )
    syslog_server_vrf: Optional[str] = Field(
        default=None,
        description="Syslog server VRF.",
        examples=["default"]
    )
    syslog_severity: Optional[str] = Field(
        default=None,
        description="Syslog severity.",
        examples=["4"]
    )
    aaa_server_conf: Optional[str] = Field(
        default=None,
        description="AAA config.",
        examples=["radius-server host 10.1.1.4"]
    )
    extra_conf_leaf: Optional[str] = Field(
        default=None,
        description="Leaf extra config.",
        examples=["no feature telnet"]
    )
    extra_conf_spine: Optional[str] = Field(
        default=None,
        description="Spine extra config.",
        examples=["feature bgp"]
    )
    netflow_enable: Optional[bool] = Field(
        default=None,
        description="NetFlow enable.",
        examples=[False]
    )
    extra_config: Optional[dict] = Field(
        default=None,
        description="Extra JSONB config.",
        examples=[{"custom_param": "value"}]
    )

    @field_validator("bgp_asn")
    @classmethod
    def _validate_bgp_asn(cls, v: str | None) -> str | None:
        return validate_bgp_asn(v) if v else v

    @field_validator("anycast_gateway_mac")
    @classmethod
    def _validate_mac(cls, v: str | None) -> str | None:
        return validate_mac(v) if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "bgp_asn": "65002",
                    "route_reflectors": 4
                }
            ]
        }
    }


class GlobalConfigRead(TimestampMixin):
    """Response body for a global config."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    global_type: str = Field(
        description="Global sub-type discriminator.",
        examples=["vxlan_evpn_ibgp"]
    )
    bgp_asn: str = Field(
        description="BGP ASN.",
        examples=["65000"]
    )
    route_reflectors: Optional[int] = Field(
        default=None,
        description="Route reflectors.",
        examples=[2]
    )
    anycast_gateway_mac: Optional[str] = Field(
        default=None,
        description="Anycast GW MAC.",
        examples=["0011.2233.4455"]
    )
    enable_nxapi_http: Optional[bool] = Field(
        default=None,
        description="NX-API HTTP.",
        examples=[False]
    )
    enable_nxapi_https: Optional[bool] = Field(
        default=None,
        description="NX-API HTTPS.",
        examples=[True]
    )
    enable_realtime_backup: Optional[bool] = Field(
        default=None,
        description="Realtime backup.",
        examples=[False]
    )
    enable_scheduled_backup: Optional[bool] = Field(
        default=None,
        description="Scheduled backup.",
        examples=[False]
    )
    inband_mgmt: Optional[bool] = Field(
        default=None,
        description="In-band management.",
        examples=[False]
    )
    bootstrap_enable: Optional[bool] = Field(
        default=None,
        description="POAP bootstrap.",
        examples=[False]
    )
    dhcp_enable: Optional[bool] = Field(
        default=None,
        description="DHCP enable.",
        examples=[False]
    )
    dns_server_ip: Optional[str] = Field(
        default=None,
        description="DNS server IP.",
        examples=["10.1.1.100"]
    )
    dns_server_vrf: Optional[str] = Field(
        default=None,
        description="DNS server VRF.",
        examples=["management"]
    )
    ntp_server_ip: Optional[str] = Field(
        default=None,
        description="NTP server IP.",
        examples=["10.1.1.101"]
    )
    ntp_server_vrf: Optional[str] = Field(
        default=None,
        description="NTP server VRF.",
        examples=["management"]
    )
    syslog_server_ip: Optional[str] = Field(
        default=None,
        description="Syslog server IP.",
        examples=["10.1.1.102"]
    )
    syslog_server_vrf: Optional[str] = Field(
        default=None,
        description="Syslog server VRF.",
        examples=["management"]
    )
    syslog_severity: Optional[str] = Field(
        default=None,
        description="Syslog severity.",
        examples=["5"]
    )
    aaa_server_conf: Optional[str] = Field(
        default=None,
        description="AAA config.",
        examples=["radius-server host 10.1.1.3 key v3ry-53cr3t"]
    )
    extra_conf_leaf: Optional[str] = Field(
        default=None,
        description="Leaf extra config.",
        examples=["feature interface-vlan"]
    )
    extra_conf_spine: Optional[str] = Field(
        default=None,
        description="Spine extra config.",
        examples=["feature ospf"]
    )
    netflow_enable: Optional[bool] = Field(
        default=None,
        description="NetFlow enable.",
        examples=[False]
    )
    extra_config: Optional[dict] = Field(
        default=None,
        description="Extra JSONB config.",
        examples=[{"overlay_mtu": 9216}]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
