# NDFC Source-of-Truth (SoT) — Complete Build & Review Prompt

> **Purpose**: This prompt provides full context and instructions for an AI coding agent
> to review, fix, and complete the NDFC SoT application.
> **Target Agent**: Claude Code (VS Code Extension)
> **Date**: March 26, 2026
> **Usage**: Open the `ndfc-sot/` folder in VS Code, open Claude Code, paste this entire prompt.

---

## AGENT INSTRUCTIONS — READ FIRST

You are reviewing and completing an **existing codebase** in the `ndfc-sot/` directory.

Your job:
1. Read all existing files in `ndfc-sot/`
2. Compare them against the requirements in this prompt
3. Identify what is missing, incomplete, or incorrect
4. Fix and complete the code — do NOT rewrite things that are already correct
5. Deliver fixes in the batches defined in Section O
6. After each batch, wait for confirmation before proceeding

---

## SECTION A — PROJECT IDENTITY

**Project Name**: `ndfc-sot`
**Language**: Python 3.11+
**Framework**: FastAPI (async)
**Database**: PostgreSQL 16 (async via `asyncpg` + SQLAlchemy 2.x)
**Migrations**: Alembic (async)
**Task Queue**: Celery + Redis (optional, keep in docker-compose but commented out)
**Containerization**: Docker Compose (local Docker Desktop)
**Purpose**: A Source-of-Truth REST API that stores the **intended network state** for
Cisco NDFC (Nexus Dashboard Fabric Controller) managed VXLAN EVPN fabrics, generates
NAC-DC compatible YAML, and deploys via Ansible.

---

## SECTION B — WHAT IS NDFC & NAC-DC

### NDFC (Nexus Dashboard Fabric Controller)
- Cisco's controller for managing data-center VXLAN EVPN fabrics
- Manages: Fabrics, Switches, Interfaces, VRFs, Networks, Underlay, Policies, Route Control
- Works on **intent-based** approach: you send the **entire desired state** (full YAML),
  NDFC computes the diff against current state, and pushes only the delta to switches
- REST API at: `https://<ndfc-ip>/appcenter/cisco/ndfc/api/v1/...`

### NAC-DC (Network as Code — Data Center)
- Cisco's open-source data model for describing NDFC fabric configurations as YAML
- Official docs: https://netascode.cisco.com/docs/data_models/vxlan/overview/
- Our Pydantic models, DB schema, and YAML output MUST align with NAC-DC structure
- The root key in NAC-DC YAML is `vxlan`

### Intent-Based Deployment Flow
```
User adds/modifies entities via API
    → Stored in PostgreSQL (SoT)
    → YAML Builder reads ALL entities for the fabric
    → Generates FULL fabric YAML (entire desired state)
    → Ansible pushes YAML to NDFC
    → NDFC diffs current vs desired
    → Only delta config pushed to physical switches
```

**CRITICAL**: When a single switch is added, we do NOT send just that switch.
We rebuild the **entire fabric YAML** including the new switch and send it all.
NDFC handles the diff.

---

## SECTION C — NAC-DC DATA MODEL HIERARCHY

The NAC-DC YAML follows this structure. Our API and DB must mirror this exactly.

```yaml
vxlan:
  fabric:
    name: "DC-FABRIC-1"
    type: "VXLAN_EVPN"

  global:
    bgp_asn: "65000"
    route_reflectors: 2
    anycast_gateway_mac: "de:ad:be:ef:fe:ed"
    enable_nxapi_http: false

  multisite:
    enabled: false

  topology:
    switches:
      - name: "SPINE-1"
        serial_number: "SAL12345678"
        role: "spine"
        routing_loopback_id: 0
        vtep_loopback_id: 1
      - name: "LEAF-1"
        serial_number: "SAL87654321"
        role: "leaf"

    interfaces:
      - switch_name: "LEAF-1"
        name: "Ethernet1/1"
        type: "trunk"
        trunk_allowed_vlans: "100-200"

    vpc_peers:
      - peer1: "LEAF-1"
        peer2: "LEAF-2"
        domain_id: 10

    fabric_links:
      - source_switch: "SPINE-1"
        source_interface: "Ethernet1/1"
        dest_switch: "LEAF-1"
        dest_interface: "Ethernet1/49"

    edge_connections:
      - switch_name: "BORDER-1"
        interface: "Ethernet1/48"
        connected_to: "EXTERNAL-ROUTER"

    tor_peers:
      - switch_name: "TOR-1"
        peer_switch: "TOR-2"

  underlay:
    general:
      replication_mode: "multicast"
      enable_trm: false
    ipv4:
      underlay_routing_loopback_ip_range: "10.250.0.0/24"
      underlay_vtep_loopback_ip_range: "10.251.0.0/24"
      underlay_rp_loopback_ip_range: "10.252.0.0/24"
      subnet_range: "10.253.0.0/24"
    ipv6:
      enable_ipv6_underlay: false
      ipv6_link_local_range: "fe80::/10"
    isis:
      authentication_enable: false
      level: "level-2"
    ospf:
      area_id: "0.0.0.0"
      authentication_enable: false
    bgp:
      authentication_enable: false
      authentication_key_type: 3
    bfd:
      enable: false
      min_tx: 50
      min_rx: 50
      multiplier: 3
    multicast:
      group_subnet: "239.1.1.0/25"
      rendezvous_points: 2
      rp_mode: "asm"

  overlay:
    vrfs:
      - name: "VRF_PROD"
        vrf_id: 50000
        vlan_id: 2000
        switches:
          - name: "LEAF-1"
          - name: "LEAF-2"

    networks:
      - name: "NET_WEB_100"
        network_id: 30001
        vlan_id: 100
        vrf_name: "VRF_PROD"
        gateway_ipv4: "10.1.100.1/24"
        suppress_arp: true
        switches:
          - name: "LEAF-1"
            ports:
              - "Ethernet1/10"

  overlay_extensions:
    vrf_lite:
      - vrf_name: "VRF_PROD"
        switch_name: "BORDER-1"
        interface: "Ethernet1/48"

    route_control:
      ipv4_prefix_lists:
        - name: "PL_DEFAULT"
          entries:
            - sequence: 10
              action: "permit"
              prefix: "0.0.0.0/0"

      ipv6_prefix_lists:
        - name: "PLv6_DEFAULT"
          entries:
            - sequence: 10
              action: "permit"
              prefix: "::/0"

      standard_community_lists:
        - name: "CL_STANDARD"
          entries:
            - sequence: 10
              action: "permit"
              community: "65000:100"

      extended_community_lists:
        - name: "CL_EXTENDED"
          entries:
            - sequence: 10
              action: "permit"
              community: "rt 65000:100"

      ip_as_path_access_lists:
        - name: "ASPATH_ALLOW"
          entries:
            - sequence: 10
              action: "permit"
              regex: "^65000_"

      route_maps:
        - name: "RM_EXPORT"
          entries:
            - sequence: 10
              action: "permit"
              match_ip_prefix_list: "PL_DEFAULT"
              set_community: "65000:200"

      ip_acls:
        - name: "ACL_PERMIT_ALL"
          type: "extended"
          entries:
            - sequence: 10
              action: "permit"
              protocol: "ip"
              source: "any"
              destination: "any"

      mac_lists:
        - name: "MAC_FILTER"
          entries:
            - sequence: 10
              action: "permit"
              mac_address: "0000.0000.0000"
              mask: "ffff.ffff.ffff"

      object_groups:
        - name: "OG_SERVERS"
          type: "ip_address"
          entries:
            - ip: "10.1.1.0/24"

      time_ranges:
        - name: "BUSINESS_HOURS"
          entries:
            - type: "periodic"
              days: "weekdays"
              start_time: "08:00"
              end_time: "18:00"

  policy:
    policies:
      - switch_name: "LEAF-1"
        template_name: "switch_freeform"
        priority: 500
        config: |
          ntp server 10.1.1.1
    groups:
      - name: "GRP_LEAF_COMMON"
        policies:
          - template_name: "switch_freeform"
            priority: 500
            config: |
              ntp server 10.1.1.1
        switches:
          - "LEAF-1"
          - "LEAF-2"
```

---

## SECTION D — COMPLETE ENTITY LIST

All 44 entities must exist as: Pydantic model + SQLAlchemy DB model + Service + Router

### D.1 Core Entities

| # | Entity | NAC-DC Path | DB Table |
|---|--------|-------------|----------|
| 1 | Fabric | `vxlan.fabric` | `fabrics` |
| 2 | Global | `vxlan.global` | `fabric_globals` |
| 3 | Multisite | `vxlan.multisite` | `multisite_configs` |

### D.2 Topology Entities

| # | Entity | NAC-DC Path | DB Table |
|---|--------|-------------|----------|
| 4 | Switch | `vxlan.topology.switches[]` | `switches` |
| 5 | Access Interface | `interfaces[]` type=access | `interfaces` |
| 6 | Access PO Interface | type=access_po | `interfaces` |
| 7 | Breakout Interface | type=breakout | `interfaces` |
| 8 | Dot1Q Tunnel Interface | type=dot1q_tunnel | `interfaces` |
| 9 | Loopback Interface | type=loopback | `interfaces` |
| 10 | Routed Interface | type=routed | `interfaces` |
| 11 | Routed PO Interface | type=routed_po | `interfaces` |
| 12 | Routed Sub-Interface | type=routed_sub | `interfaces` |
| 13 | Trunk Interface | type=trunk | `interfaces` |
| 14 | Trunk PO Interface | type=trunk_po | `interfaces` |
| 15 | vPC Peer | `vxlan.topology.vpc_peers[]` | `vpc_peers` |
| 16 | Fabric Link | `vxlan.topology.fabric_links[]` | `fabric_links` |
| 17 | Edge Connection | `vxlan.topology.edge_connections[]` | `edge_connections` |
| 18 | ToR Peer | `vxlan.topology.tor_peers[]` | `tor_peers` |

### D.3 Underlay Entities

| # | Entity | NAC-DC Path | DB Table |
|---|--------|-------------|----------|
| 19 | Underlay General | `vxlan.underlay.general` | `underlay_general` |
| 20 | Underlay IPv4 | `vxlan.underlay.ipv4` | `underlay_ipv4` |
| 21 | Underlay IPv6 | `vxlan.underlay.ipv6` | `underlay_ipv6` |
| 22 | Underlay IS-IS | `vxlan.underlay.isis` | `underlay_isis` |
| 23 | Underlay OSPF | `vxlan.underlay.ospf` | `underlay_ospf` |
| 24 | Underlay BGP | `vxlan.underlay.bgp` | `underlay_bgp` |
| 25 | Underlay BFD | `vxlan.underlay.bfd` | `underlay_bfd` |
| 26 | Underlay Multicast | `vxlan.underlay.multicast` | `underlay_multicast` |

### D.4 Overlay Entities

| # | Entity | NAC-DC Path | DB Table |
|---|--------|-------------|----------|
| 27 | VRF | `vxlan.overlay.vrfs[]` | `vrfs` |
| 28 | VRF Switch Attach | `vrfs[].switches[]` | `vrf_switch_attachments` |
| 29 | Network | `vxlan.overlay.networks[]` | `networks` |
| 30 | Network Switch Attach | `networks[].switches[]` | `network_switch_attachments` |

### D.5 Overlay Extensions

| # | Entity | NAC-DC Path | DB Table |
|---|--------|-------------|----------|
| 31 | VRF Lite Extension | `vxlan.overlay_extensions.vrf_lite[]` | `vrf_lite_extensions` |
| 32 | IPv4 Prefix List | `route_control.ipv4_prefix_lists[]` | `ipv4_prefix_lists` |
| 33 | IPv6 Prefix List | `route_control.ipv6_prefix_lists[]` | `ipv6_prefix_lists` |
| 34 | Standard Community List | `route_control.standard_community_lists[]` | `standard_community_lists` |
| 35 | Extended Community List | `route_control.extended_community_lists[]` | `extended_community_lists` |
| 36 | AS-Path Access List | `route_control.ip_as_path_access_lists[]` | `as_path_access_lists` |
| 37 | Route Map | `route_control.route_maps[]` | `route_maps` |
| 38 | IP ACL | `route_control.ip_acls[]` | `ip_acls` |
| 39 | MAC List | `route_control.mac_lists[]` | `mac_lists` |
| 40 | Object Group | `route_control.object_groups[]` | `object_groups` |
| 41 | Time Range | `route_control.time_ranges[]` | `time_ranges` |

### D.6 Policy Entities

| # | Entity | NAC-DC Path | DB Table |
|---|--------|-------------|----------|
| 42 | Policy | `vxlan.policy.policies[]` | `policies` |
| 43 | Policy Group | `vxlan.policy.groups[]` | `policy_groups` |
| 44 | Policy Group Assignment | `groups[].switches[]` | `policy_group_assignments` |

---

## SECTION E — NAC-DC FIELD SPECIFICATIONS

### E.1 Fabric

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `name` | string | Yes | `^[a-zA-Z][a-zA-Z0-9_-]{0,63}$` |
| `type` | enum | Yes | `VXLAN_EVPN`, `MSD`, `MCFG`, `ISN`, `External`, `eBGP_VXLAN` |

### E.2 Global

**IMPORTANT**: Global has 3 sub-types based on fabric type.
Use a `global_type` discriminator field in the DB and Pydantic models:
- `vxlan_evpn_ibgp` — for VXLAN_EVPN fabrics with iBGP
- `vxlan_evpn_ebgp` — for eBGP_VXLAN fabrics
- `external` — for External fabric type

Fields below apply to `vxlan_evpn_ibgp` (most common). Store type-specific fields
in a JSONB `extra_config` column for the other types.

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `global_type` | enum | Yes | `vxlan_evpn_ibgp` |
| `bgp_asn` | string | Yes | — |
| `route_reflectors` | int | No | `2` |
| `anycast_gateway_mac` | string | No | — |
| `enable_nxapi_http` | bool | No | `false` |
| `enable_nxapi_https` | bool | No | `true` |
| `enable_realtime_backup` | bool | No | `false` |
| `enable_scheduled_backup` | bool | No | `false` |
| `inband_mgmt` | bool | No | `false` |
| `bootstrap_enable` | bool | No | `false` |
| `dhcp_enable` | bool | No | `false` |
| `dns_server_ip` | string | No | — |
| `dns_server_vrf` | string | No | `management` |
| `ntp_server_ip` | string | No | — |
| `ntp_server_vrf` | string | No | `management` |
| `syslog_server_ip` | string | No | — |
| `syslog_server_vrf` | string | No | `management` |
| `syslog_severity` | string | No | `5` |
| `aaa_server_conf` | string | No | — |
| `extra_conf_leaf` | string | No | — |
| `extra_conf_spine` | string | No | — |
| `netflow_enable` | bool | No | `false` |

### E.3 Multisite

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `enabled` | bool | No | `false` |
| `multisite_bgw_ip` | string | No | — |
| `dci_subnet_range` | string | No | — |
| `dci_subnet_mask` | int | No | — |
| `delay_restore` | int | No | `300` |

### E.4 Switch

**Switch Roles** (enum): `spine`, `leaf`, `border`, `border_spine`, `border_gateway`,
`border_gateway_spine`, `super_spine`, `border_super_spine`, `access`

| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| `name` | string | Yes | — | — |
| `serial_number` | string | No | `^[a-zA-Z0-9_.:-]{1,16}$` | — |
| `role` | enum | No | see above | `leaf` |
| `routing_loopback_id` | int | No | `0-1023` | `0` |
| `vtep_loopback_id` | int | No | `0-1023` | `1` |
| `routing_loopback_ipv4` | string | No | IPv4 | — |
| `routing_loopback_ipv6` | string | No | IPv6 | — |
| `vtep_loopback_ipv4` | string | No | IPv4 | — |
| `mgmt_ip` | string | No | IPv4 | — |
| `mgmt_gw` | string | No | IPv4 | — |
| `seed_ip` | string | No | IPv4 | — |
| `max_paths` | int | No | `1-64` | — |
| `system_nve_id` | int | No | `1-4` | `1` |
| `data_link` | string | No | — | — |
| `vpc_domain_id` | int | No | — | — |
| `vpc_peer_link` | string | No | — | — |
| `vpc_peer_ip` | string | No | — | — |
| `freeform_config` | string | No | — | — |

### E.5 Interface Types

All interfaces share base fields:

| Field | Type | Required |
|-------|------|----------|
| `switch_name` | string | Yes |
| `name` | string | Yes |
| `type` | enum | Yes |
| `description` | string | No |
| `admin_state` | bool | No |
| `mtu` | int | No |
| `speed` | string | No |
| `freeform_config` | string | No |

**CRITICAL YAML KEY**: Trunk interface allowed VLANs YAML key MUST be `trunk_allowed_vlans`
(NOT `trunk_vlans`). This is the exact NAC-DC field name used by the Ansible collection.

Type-specific fields stored in JSONB `type_config` column:

#### Access Interface
| `access_vlan` | int | VLAN ID 1-4094 |

#### Access Port-Channel
| `access_vlan` | int | VLAN ID |
| `po_id` | int | Port-channel ID |
| `member_interfaces` | list[string] | Member interfaces |
| `mode` | enum | `active`, `passive`, `on` |
| `vpc_id` | int | vPC ID (optional) |

#### Breakout Interface
| `breakout_mode` | string | e.g., `10g-4x` |

#### Dot1Q Tunnel Interface
| `tunnel_vlan` | int | Outer VLAN |

#### Loopback Interface
| `loopback_id` | int | 0-1023 |
| `ipv4_address` | string | IPv4/mask |
| `ipv6_address` | string | IPv6/mask |
| `vrf` | string | VRF name |
| `route_map_tag` | string | Route-map |

#### Routed Interface
| `ipv4_address` | string | IPv4/mask |
| `ipv6_address` | string | IPv6/mask |
| `vrf` | string | VRF name |
| `route_map_tag` | string | Route-map |
| `ospf_area` | string | OSPF area |
| `ospf_auth_enable` | bool | OSPF auth |
| `ospf_auth_key` | string | OSPF auth key |

#### Routed Port-Channel
Same as Routed + `po_id`, `member_interfaces`, `mode`

#### Routed Sub-Interface
Same as Routed + `parent_interface`, `dot1q_vlan`

#### Trunk Interface
| `trunk_allowed_vlans` | string | e.g., `100-200,300` |
| `native_vlan` | int | Native VLAN ID |

#### Trunk Port-Channel
Same as Trunk + `po_id`, `member_interfaces`, `mode`, `vpc_id`

### E.6 vPC Peer

| Field | Type | Required |
|-------|------|----------|
| `peer1` | string | Yes |
| `peer2` | string | Yes |
| `domain_id` | int | Yes |
| `peer_link_po_id` | int | No |
| `peer_link_members` | list[string] | No |
| `keepalive_vrf` | string | No |
| `keepalive_ip_peer1` | string | No |
| `keepalive_ip_peer2` | string | No |

### E.7 Fabric Link

| Field | Type | Required |
|-------|------|----------|
| `source_switch` | string | Yes |
| `source_interface` | string | Yes |
| `dest_switch` | string | Yes |
| `dest_interface` | string | Yes |
| `link_template` | string | No |
| `mtu` | int | No |
| `freeform_config` | string | No |

### E.8 Edge Connection

| Field | Type | Required |
|-------|------|----------|
| `switch_name` | string | Yes |
| `interface` | string | Yes |
| `connected_to` | string | No |
| `peer_ip` | string | No |
| `bgp_peer_asn` | string | No |
| `vrf` | string | No |
| `description` | string | No |
| `freeform_config` | string | No |

### E.9 ToR Peer

| Field | Type | Required |
|-------|------|----------|
| `switch_name` | string | Yes |
| `peer_switch` | string | Yes |
| `link_interfaces` | list[string] | No |

### E.10 Underlay General

| Field | Type | Default |
|-------|------|---------|
| `replication_mode` | enum | `multicast` |
| `enable_trm` | bool | `false` |
| `underlay_routing_protocol` | enum | `ospf` |
| `link_state_routing_tag` | string | `UNDERLAY` |
| `enable_pvlan` | bool | `false` |
| `enable_netflow` | bool | `false` |
| `stp_root_bridge_option` | enum | `unmanaged` |
| `brownfield_import` | bool | `false` |

### E.11 Underlay IPv4

| Field | Type | Default |
|-------|------|---------|
| `underlay_routing_loopback_ip_range` | string | `10.2.0.0/22` |
| `underlay_vtep_loopback_ip_range` | string | `10.3.0.0/22` |
| `underlay_rp_loopback_ip_range` | string | `10.254.254.0/24` |
| `subnet_range` | string | `10.4.0.0/16` |
| `underlay_subnet_mask` | int | `30` |

### E.12 Underlay IPv6

| Field | Type | Default |
|-------|------|---------|
| `enable_ipv6_underlay` | bool | `false` |
| `ipv6_link_local_range` | string | `fe80::/10` |
| `underlay_v6_routing_loopback_range` | string | — |
| `underlay_v6_vtep_loopback_range` | string | — |

### E.13 Underlay IS-IS

| Field | Type | Default |
|-------|------|---------|
| `authentication_enable` | bool | `false` |
| `authentication_key` | string | — |
| `authentication_key_id` | int | — |
| `overload_bit` | bool | `false` |
| `level` | enum | `level-2` |
| `network_type` | enum | `p2p` |

### E.14 Underlay OSPF

| Field | Type | Default |
|-------|------|---------|
| `area_id` | string | `0.0.0.0` |
| `authentication_enable` | bool | `false` |
| `authentication_key` | string | — |
| `authentication_key_id` | int | — |

### E.15 Underlay BGP

| Field | Type | Default |
|-------|------|---------|
| `authentication_enable` | bool | `false` |
| `authentication_key_type` | int | `3` |
| `authentication_key` | string | — |

### E.16 Underlay BFD

| Field | Type | Default |
|-------|------|---------|
| `enable` | bool | `false` |
| `min_tx` | int | `50` |
| `min_rx` | int | `50` |
| `multiplier` | int | `3` |
| `enable_ibgp` | bool | `false` |
| `enable_ospf` | bool | `false` |
| `enable_isis` | bool | `false` |
| `enable_pim` | bool | `false` |

### E.17 Underlay Multicast

| Field | Type | Default |
|-------|------|---------|
| `group_subnet` | string | `239.1.1.0/25` |
| `rendezvous_points` | int | `2` |
| `rp_mode` | enum | `asm` |
| `underlay_rp_loopback_id` | int | `254` |
| `trm_enable` | bool | `false` |
| `trm_bgw_msite_enable` | bool | `false` |

### E.18 Overlay VRF

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `name` | string | Yes | — |
| `vrf_id` | int | Yes | — |
| `vlan_id` | int | Yes | — |
| `vrf_description` | string | No | — |
| `route_target_both` | bool | No | `false` |
| `route_target_import` | string | No | — |
| `route_target_export` | string | No | — |
| `route_target_import_evpn` | string | No | — |
| `route_target_export_evpn` | string | No | — |
| `ipv6_link_local_flag` | bool | No | `true` |
| `max_bgp_paths` | int | No | `1` |
| `max_ibgp_paths` | int | No | `2` |
| `advertise_host_routes` | bool | No | `false` |
| `advertise_default_route` | bool | No | `true` |
| `enable_trm` | bool | No | `false` |
| `rp_address` | string | No | — |
| `rp_external` | bool | No | `false` |
| `underlay_mcast_ip` | string | No | — |
| `overlay_mcast_group` | string | No | — |
| `netflow_enable` | bool | No | `false` |
| `no_rp` | bool | No | `false` |
| `route_map_in` | string | No | — |
| `route_map_out` | string | No | — |
| `freeform_config` | string | No | — |

**VRF Switch Attachment:**
| `name` | string | Yes | Switch hostname |
| `vrf_lite` | list | No | VRF Lite extension config |
| `freeform_config` | string | No | Per-switch CLI |

### E.19 Overlay Network

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `name` | string | Yes | — |
| `network_id` | int | Yes | — |
| `vlan_id` | int | Yes | — |
| `vlan_name` | string | No | — |
| `vrf_name` | string | Conditional | — |
| `gateway_ipv4` | string | No | — |
| `gateway_ipv6` | string | No | — |
| `suppress_arp` | bool | No | `false` |
| `enable_ir` | bool | No | `false` |
| `mtu` | int | No | `9216` |
| `routing_tag` | int | No | `12345` |
| `is_l2_only` | bool | No | `false` |
| `multicast_group` | string | No | — |
| `dhcp_server_addr_1` | string | No | — |
| `dhcp_server_addr_2` | string | No | — |
| `dhcp_server_addr_3` | string | No | — |
| `dhcp_server_vrf` | string | No | — |
| `loopback_id` | int | No | — |
| `enable_trm` | bool | No | `false` |
| `route_map_in` | string | No | — |
| `netflow_enable` | bool | No | `false` |
| `freeform_config` | string | No | — |

**Network Switch Attachment:**
| `name` | string | Yes | Switch hostname |
| `ports` | list[string] | No | Attached ports |
| `freeform_config` | string | No | Per-switch CLI |

### E.20 VRF Lite Extension

| Field | Type | Required |
|-------|------|----------|
| `vrf_name` | string | Yes |
| `switch_name` | string | Yes |
| `interface` | string | Yes |
| `ipv4_neighbor` | string | No |
| `ipv6_neighbor` | string | No |
| `peer_vrf` | string | No |
| `dot1q_vlan` | int | No |
| `bgp_peer_asn` | string | No |
| `freeform_config` | string | No |

### E.21 Route Control Entities

#### IPv4 / IPv6 Prefix List
| `name` | string | List name |
| `description` | string | Optional |
| `entries[].sequence` | int | Sequence |
| `entries[].action` | enum | `permit`/`deny` |
| `entries[].prefix` | string | IP prefix |
| `entries[].ge` | int | Greater-or-equal mask |
| `entries[].le` | int | Less-or-equal mask |

#### Standard Community List
| `name` | string | List name |
| `entries[].sequence` | int | Sequence |
| `entries[].action` | enum | `permit`/`deny` |
| `entries[].community` | string | e.g., `65000:100` |

#### Extended Community List
| `name` | string | List name |
| `entries[].sequence` | int | Sequence |
| `entries[].action` | enum | `permit`/`deny` |
| `entries[].community` | string | e.g., `rt 65000:100` |

#### IP AS-Path Access List
| `name` | string | List name |
| `entries[].sequence` | int | Sequence |
| `entries[].action` | enum | `permit`/`deny` |
| `entries[].regex` | string | AS-path regex |

#### Route Map
| `name` | string | Route-map name |
| `entries[].sequence` | int | Sequence |
| `entries[].action` | enum | `permit`/`deny` |
| `entries[].match_ip_prefix_list` | string | Match IPv4 prefix list |
| `entries[].match_ipv6_prefix_list` | string | Match IPv6 prefix list |
| `entries[].match_community_list` | string | Match community list |
| `entries[].match_as_path` | string | Match AS-path list |
| `entries[].match_tag` | int | Match tag |
| `entries[].match_interface` | string | Match interface |
| `entries[].set_community` | string | Set community |
| `entries[].set_community_additive` | bool | Additive |
| `entries[].set_local_preference` | int | Set local-pref |
| `entries[].set_metric` | int | Set metric |
| `entries[].set_next_hop` | string | Set next-hop |
| `entries[].set_origin` | enum | `igp`/`egp`/`incomplete` |
| `entries[].set_tag` | int | Set tag |
| `entries[].set_weight` | int | Set weight |

#### IP ACL
| `name` | string | ACL name |
| `type` | enum | `standard`/`extended` |
| `entries[].sequence` | int | Sequence |
| `entries[].action` | enum | `permit`/`deny` |
| `entries[].protocol` | string | IP protocol |
| `entries[].source` | string | Source |
| `entries[].source_port` | string | Source port |
| `entries[].destination` | string | Destination |
| `entries[].destination_port` | string | Destination port |
| `entries[].dscp` | int | DSCP value |
| `entries[].time_range` | string | Time-range name |

#### MAC List
| `name` | string | List name |
| `entries[].sequence` | int | Sequence |
| `entries[].action` | enum | `permit`/`deny` |
| `entries[].mac_address` | string | MAC address |
| `entries[].mask` | string | MAC mask |

#### Object Group
| `name` | string | Group name |
| `type` | enum | `ip_address`/`network`/`port` |
| `entries[]` | varies | Type-dependent |

#### Time Range
| `name` | string | Time range name |
| `entries[].type` | enum | `absolute`/`periodic` |
| `entries[].start_time` | string | Start time |
| `entries[].end_time` | string | End time |
| `entries[].days` | string | Days (for periodic) |

### E.22 Policy

| Field | Type | Required |
|-------|------|----------|
| `switch_name` | string | Yes |
| `template_name` | string | Yes |
| `priority` | int | No (default 500) |
| `description` | string | No |
| `config` | string | No |

### E.23 Policy Group

| Field | Type | Required |
|-------|------|----------|
| `name` | string | Yes |
| `policies` | list | Yes |
| `switches` | list[string] | Yes |

**Policy Group Assignment**: stores `switch_name` as string (NOT UUID FK),
because switches may be referenced by hostname before they are registered in DB.

---

## SECTION F — API DESIGN REQUIREMENTS

### F.1 Base Configuration

| Item | Value |
|------|-------|
| Base URL | `/api/v1` |
| Auth | API key via `X-API-Key` header |
| Response format | JSON |
| ID type | UUID v4 |
| Timestamps | `created_at`, `updated_at` (auto, ISO 8601) |

### F.2 API Key Authentication

- Read from environment variable: `NDFC_SOT_API_KEY`
- Support comma-separated list for multiple keys: `KEY1,KEY2,KEY3`
- Validate in `app/auth.py` as a FastAPI dependency
- Return `401 Unauthorized` if key is missing or invalid
- Example `config.py`:
```python
class Settings(BaseSettings):
    api_keys: list[str] = Field(default_factory=list)
    
    @validator("api_keys", pre=True)
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v
    
    model_config = SettingsConfigDict(env_prefix="NDFC_SOT_")
```

### F.3 Standard Error Response

ALL error responses must use this format — no exceptions:
```json
{
  "detail": "Switch LEAF-1 not found in fabric DC-1",
  "error_code": "NOT_FOUND"
}
```

Error codes: `NOT_FOUND`, `ALREADY_EXISTS`, `VALIDATION_ERROR`, `DEPENDENCY_ERROR`

### F.4 Endpoint Design Pattern

Every list entity (switches, VRFs, networks, etc.) must have:
```
POST   /api/v1/{resource}                     → Create one
POST   /api/v1/{resource}/bulk                → Create multiple
GET    /api/v1/{resource}/fabric/{fabric_id}  → List by fabric
GET    /api/v1/{resource}/{id}                → Get by ID
PATCH  /api/v1/{resource}/{id}                → Partial update
DELETE /api/v1/{resource}/{id}                → Delete
```

Every 1:1 entity (global, underlay sections) must have:
```
GET    /api/v1/{resource}/fabric/{fabric_id}  → Get
PUT    /api/v1/{resource}/fabric/{fabric_id}  → Create or update (upsert)
DELETE /api/v1/{resource}/fabric/{fabric_id}  → Delete
```

### F.5 Import Endpoints

```
POST /api/v1/import
Body: { entire NAC-DC structure as JSON }
Behavior: Upsert all entities
Response: { summary of created/updated counts per entity type }

POST /api/v1/import/switches
POST /api/v1/import/vrfs
POST /api/v1/import/networks
Body: { "fabric_name": "...", "items": [...] }
```

### F.6 YAML & Deploy Endpoints

```
GET  /api/v1/yaml/{fabric_id}           → Full fabric YAML preview (returns JSON)
GET  /api/v1/yaml/{fabric_id}/download  → Download as .yaml file
POST /api/v1/yaml/{fabric_id}/generate  → Write YAML to disk

POST /api/v1/deploy/{fabric_id}         → Generate YAML + run Ansible
Body: { "fabric_id": "uuid", "dry_run": false }
Response: { "status": "success|failed", "output": "ansible output" }
```

### F.7 Swagger UI Requirements

- Title: "NDFC Source-of-Truth API"
- Description: detailed overview for network engineers
- Tags: group endpoints by domain (Fabric, Global, Topology, Underlay, Overlay, Route Control, Policy, Import, YAML/Deploy)
- Every Pydantic model must have `Field(description="...")` on every field
- Every Pydantic model must have `model_config` with `json_schema_extra` containing realistic example values

---

## SECTION G — DATABASE & ORM REQUIREMENTS

### G.1 PostgreSQL Rules
- Version: 16
- Auth: `trust` (no password for local dev)
- Database name: `ndfc_sot`
- All tables: UUID primary keys (`gen_random_uuid()`)
- All tables: `created_at` and `updated_at` timestamps
- JSONB columns for entries (prefix lists, route maps, type_config)
- Foreign keys with `CASCADE` delete where child cannot exist without parent

### G.2 SQLAlchemy Rules
- Async engine via `asyncpg`
- SQLAlchemy 2.x `Mapped[]` type hints
- `lazy="selectin"` for relationships

### G.3 Alembic Rules
- Single migration for initial schema
- Async migration support
- `startup.sh` runs `alembic upgrade head` before starting uvicorn

---

## SECTION H — DOCKER COMPOSE REQUIREMENTS

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ndfc_sot
      POSTGRES_HOST_AUTH_METHOD: trust
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck: pg_isready

  app:
    build: .
    ports: ["8000:8000"]
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres@postgres:5432/ndfc_sot
      NDFC_SOT_API_KEY: "dev-api-key-change-in-production"
    entrypoint: ["/app/startup.sh"]

  # redis: (commented out — for future Celery)
  # celery-worker: (commented out — for future Celery)
```

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x startup.sh
CMD ["/app/startup.sh"]
```

### startup.sh
```bash
#!/bin/bash
set -e
echo "Running migrations..."
alembic upgrade head
echo "Starting server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## SECTION I — YAML BUILDER REQUIREMENTS

The YAML Builder (`app/services/yaml_builder.py`) must:

1. Accept a `fabric_id` (UUID)
2. Query ALL entities for that fabric from PostgreSQL
3. Build a Python dict matching the exact NAC-DC YAML structure
4. Return dict for preview OR write to disk as `{fabric_name}.yaml`
5. The output YAML must be directly consumable by `cisco.dcnm` Ansible collection

**NOTE**: The Ansible collection package name is `cisco.dcnm` (legacy name still used
even though NDFC replaced DCNM). Import in playbooks as `cisco.dcnm`.

Output structure:
```python
{
  "vxlan": {
    "fabric": {...},
    "global": {...},
    "multisite": {...},        # only if enabled
    "topology": {
      "switches": [...],
      "interfaces": [...],
      "vpc_peers": [...],
      "fabric_links": [...],
      "edge_connections": [...],
      "tor_peers": [...]
    },
    "underlay": {
      "general": {...},
      "ipv4": {...},
      "ipv6": {...},
      "isis": {...},
      "ospf": {...},
      "bgp": {...},
      "bfd": {...},
      "multicast": {...}
    },
    "overlay": {
      "vrfs": [...],
      "networks": [...]
    },
    "overlay_extensions": {
      "vrf_lite": [...],
      "route_control": {
        "ipv4_prefix_lists": [...],
        "ipv6_prefix_lists": [...],
        "standard_community_lists": [...],
        "extended_community_lists": [...],
        "ip_as_path_access_lists": [...],
        "route_maps": [...],
        "ip_acls": [...],
        "mac_lists": [...],
        "object_groups": [...],
        "time_ranges": [...]
      }
    },
    "policy": {
      "policies": [...],
      "groups": [...]
    }
  }
}
```

**Omit empty sections** — if no VRF Lite extensions exist, omit `vrf_lite` key entirely.

---

## SECTION J — ANSIBLE DEPLOYER REQUIREMENTS

`app/services/ansible_deployer.py` must:

1. Call `yaml_builder.py` to generate the fabric YAML dict
2. Write YAML to disk: `./ansible/host_vars/{fabric_name}.yaml`
3. Run Ansible playbook via `ansible_runner`:
```python
import ansible_runner

result = ansible_runner.run(
    private_data_dir="./ansible",
    playbook="ndfc_deploy.yml",
    extravars={"fabric_name": fabric_name}
)
```
4. Return stdout, stderr, and return code
5. The Ansible playbook template (`ansible/ndfc_deploy.yml`):
```yaml
---
- name: Deploy NDFC Fabric via NAC-DC
  hosts: localhost
  gather_facts: false
  roles:
    - cisco.dcnm.dcnm_rest
  vars_files:
    - "host_vars/{{ fabric_name }}.yaml"
```

---

## SECTION K — FILE STRUCTURE

```
ndfc-sot/
├── docker-compose.yaml
├── Dockerfile
├── startup.sh
├── requirements.txt
├── pyproject.toml
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
├── ansible/
│   ├── ndfc_deploy.yml
│   └── host_vars/           # generated YAML files land here
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth.py
│   ├── exceptions.py
│   ├── dependencies.py
│   │
│   ├── db_models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── fabric.py
│   │   ├── switch.py
│   │   ├── interface.py
│   │   ├── vrf.py
│   │   ├── network.py
│   │   ├── underlay.py
│   │   ├── topology.py
│   │   ├── overlay_extensions.py
│   │   ├── route_control.py
│   │   └── policy.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── fabric.py
│   │   ├── inventory.py
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── access.py
│   │   │   ├── access_po.py
│   │   │   ├── breakout.py
│   │   │   ├── dot1q_tunnel.py
│   │   │   ├── loopback.py
│   │   │   ├── routed.py
│   │   │   ├── routed_po.py
│   │   │   ├── routed_sub.py
│   │   │   ├── trunk.py
│   │   │   └── trunk_po.py
│   │   ├── topology.py
│   │   ├── underlay/
│   │   │   ├── __init__.py
│   │   │   ├── general.py
│   │   │   ├── ipv4.py
│   │   │   ├── ipv6.py
│   │   │   ├── isis.py
│   │   │   ├── ospf.py
│   │   │   ├── bgp.py
│   │   │   ├── bfd.py
│   │   │   └── multicast.py
│   │   ├── overlay/
│   │   │   ├── __init__.py
│   │   │   ├── vrf.py
│   │   │   └── network.py
│   │   ├── overlay_extensions/
│   │   │   ├── __init__.py
│   │   │   └── vrf_lite.py
│   │   ├── route_control/
│   │   │   ├── __init__.py
│   │   │   ├── ip_prefix_list.py
│   │   │   ├── community_list.py
│   │   │   ├── as_path_list.py
│   │   │   ├── route_map.py
│   │   │   ├── ip_acl.py
│   │   │   ├── mac_list.py
│   │   │   ├── object_group.py
│   │   │   └── time_range.py
│   │   ├── policy/
│   │   │   ├── __init__.py
│   │   │   └── policy.py
│   │   ├── import_models.py
│   │   ├── yaml_models.py
│   │   └── deploy.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── fabric_service.py
│   │   ├── global_service.py
│   │   ├── switch_service.py
│   │   ├── interface_service.py
│   │   ├── vrf_service.py
│   │   ├── network_service.py
│   │   ├── underlay_service.py
│   │   ├── topology_service.py
│   │   ├── overlay_extension_service.py
│   │   ├── route_control_service.py
│   │   ├── policy_service.py
│   │   ├── import_service.py
│   │   ├── yaml_builder.py
│   │   └── ansible_deployer.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── fabric.py
│   │   ├── switches.py
│   │   ├── interfaces.py
│   │   ├── topology.py
│   │   ├── underlay.py
│   │   ├── vrfs.py
│   │   ├── networks.py
│   │   ├── overlay_extensions.py
│   │   ├── route_control.py
│   │   ├── policy.py
│   │   ├── import_router.py
│   │   └── yaml_deploy.py
│   │
│   ├── validators/
│   │   ├── __init__.py
│   │   └── referential.py
│   │
│   └── tasks/
│       ├── __init__.py
│       ├── celery_app.py
│       └── deploy_tasks.py
│
└── tests/
    ├── conftest.py
    └── test_models/
```

---

## SECTION L — SERVICE LAYER PATTERN

```python
class EntityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[Model]: ...
    async def get_by_id(self, entity_id: UUID) -> Model: ...
    async def create(self, payload: CreateSchema) -> Model: ...
    async def create_bulk(self, payloads: list[CreateSchema]) -> list[Model]: ...
    async def update(self, entity_id: UUID, payload: UpdateSchema) -> Model: ...
    async def upsert(self, payload: CreateSchema) -> Model: ...
    async def delete(self, entity_id: UUID) -> None: ...
```

Natural keys for upsert:
- Fabric: `name`
- Switch: `fabric_id` + `name`
- Interface: `switch_id` + `name`
- VRF: `fabric_id` + `name`
- Network: `fabric_id` + `name`
- Underlay sections: `fabric_id` (1:1)
- All route control: `fabric_id` + `name`
- Policy: `fabric_id` + `switch_name` + `template_name`

---

## SECTION M — DEPENDENCIES (requirements.txt)

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy[asyncio]>=2.0.36
asyncpg>=0.30.0
alembic>=1.14.0
pydantic>=2.10.0
pydantic-settings>=2.7.0
python-multipart>=0.0.18
httpx>=0.28.0
pyyaml>=6.0.2
celery>=5.4.0
redis>=5.2.1
ansible-runner>=2.4.0
```

---

## SECTION N — CRITICAL RULES FOR THE AGENT

1. **Review existing code first** — do not rewrite what is already correct
2. **DO NOT hallucinate fields** — only use fields listed in Section E
3. **DO NOT skip entities** — all 44 entities in Section D must be implemented
4. **Match NAC-DC YAML structure exactly** — output must work with `cisco.dcnm` collection
5. **YAML key for trunk vlans is `trunk_allowed_vlans`** — NOT `trunk_vlans`
6. **Ansible collection is `cisco.dcnm`** — not `cisco.ndfc`
7. **Global entity has 3 types** — use `global_type` discriminator field
8. **Policy group switches stored as `switch_name` string** — NOT UUID FK
9. **Every Pydantic field must have `Field(description="...")`**
10. **Every Pydantic model must have `model_config` with `json_schema_extra`**
11. **Use async everywhere** — async routes, async services, async DB
12. **PostgreSQL trust auth** — no passwords in development
13. **Single `interfaces` table** with `type` discriminator + JSONB `type_config`
14. **Entries stored as JSONB arrays** (prefix list entries, route map entries, etc.)
15. **Foreign keys use CASCADE delete** where child cannot exist without parent
16. **Startup script must run migrations before server start**
17. **Docker Compose must work with `docker-compose up --build`**
18. **Redis/Celery commented out** in docker-compose
19. **Standard error format**: `{"detail": "...", "error_code": "..."}`
20. **API key from env var** `NDFC_SOT_API_KEY`, comma-separated for multiple keys
21. **Omit empty YAML sections** in YAML builder output
22. **The audience is network engineers** — use networking terminology in descriptions

---

## SECTION O — REVIEW AND FIX ORDER

Review the existing code and deliver fixes in this order.
**Wait for confirmation after each batch.**

### Batch 1 — Infrastructure Review
Check and fix:
- `Dockerfile`, `docker-compose.yaml`, `startup.sh`, `requirements.txt`
- `alembic.ini`, `alembic/env.py`
- `app/config.py` — must include API key config as specified in F.2
- `app/auth.py` — must validate `X-API-Key` against env var

### Batch 2 — Pydantic Models Review
Check and fix all models in `app/models/`:
- Verify all 44 entities have Create/Read/Update schemas
- Verify `global_type` discriminator exists on Global model
- Verify trunk interface uses `trunk_allowed_vlans` (not `trunk_vlans`)
- Verify every field has `Field(description="...")`
- Verify every model has `json_schema_extra` with examples
- Add any missing models

### Batch 3 — DB Models & Migration Review
Check and fix all models in `app/db_models/`:
- Verify all 44 entities have SQLAlchemy ORM models
- Verify single `interfaces` table with `type` + `type_config` JSONB
- Verify `multisite_configs` table exists
- Verify `global_type` column exists on `fabric_globals`
- Verify all FK CASCADE rules
- Fix/regenerate `alembic/versions/001_initial_schema.py` if needed

### Batch 4 — Services Review
Check and fix all services in `app/services/`:
- Verify upsert logic uses natural keys per Section L
- Verify `yaml_builder.py` matches Section I output structure exactly
- Verify `yaml_builder.py` omits empty sections
- Add `ansible_deployer.py` if missing or incomplete (per Section J)
- Add `import_service.py` if missing or incomplete

### Batch 5 — Routers Review
Check and fix all routers in `app/routers/`:
- Verify all endpoint patterns match Section F.4
- Verify all routers use standard error format from F.3
- Verify `/deploy/{fabric_id}` endpoint exists in `yaml_deploy.py`
- Verify `app/main.py` includes all routers with correct tags

### Batch 6 — End-to-End Verification
Run through the test checklist in Section P mentally and flag any issues.

---

## SECTION P — TESTING CHECKLIST

After fixes, verify:

### P.1 Docker Start
```bash
docker-compose up --build
# App at http://localhost:8000
# Swagger at http://localhost:8000/docs
# Postgres at localhost:5432
```

### P.2 End-to-End Flow
```
1. POST /api/v1/fabrics
   Body: {"name": "DC-1", "type": "VXLAN_EVPN"}
   → 201 Created

2. PUT /api/v1/globals/fabric/{fabric_id}
   Body: {"global_type": "vxlan_evpn_ibgp", "bgp_asn": "65001"}
   → 200 OK

3. POST /api/v1/switches
   Body: {"fabric_id": "...", "name": "SPINE-1", "role": "spine"}
   → 201 Created

4. POST /api/v1/switches
   Body: {"fabric_id": "...", "name": "LEAF-1", "role": "leaf"}
   → 201 Created

5. PUT /api/v1/underlay/general/fabric/{fabric_id}
   Body: {"replication_mode": "multicast", "underlay_routing_protocol": "ospf"}

6. POST /api/v1/vrfs
   Body: {"fabric_id": "...", "name": "VRF_PROD", "vrf_id": 50000, "vlan_id": 2000}

7. POST /api/v1/networks
   Body: {"fabric_id": "...", "name": "NET_WEB", "network_id": 30001,
          "vlan_id": 100, "vrf_name": "VRF_PROD", "gateway_ipv4": "10.1.100.1/24"}

8. GET /api/v1/yaml/{fabric_id}
   → Returns full NAC-DC YAML with all entities
   → YAML keys match NAC-DC spec exactly (trunk_allowed_vlans, not trunk_vlans)

9. POST /api/v1/import
   Body: (full NAC-DC JSON)
   → 200 {"fabrics_created": 1, "switches_created": 2, ...}
```
