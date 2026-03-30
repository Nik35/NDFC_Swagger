# 🌐 NDFC Source-of-Truth (SoT) — Complete API Documentation

> **Version:** 1.0.0  
> **Base URL:** `http://<host>:8000/api/v1`  
> **Authentication:** API Key via `X-API-Key` header  
> **Content-Type:** `application/json`

---

## 📑 Table of Contents

1. [Authentication](#-authentication)
2. [Common Patterns](#-common-patterns)
3. [Health Check](#-health-check)
4. [Fabrics](#-fabrics)
5. [Switches (Inventory)](#-switches-inventory)
6. [VRFs](#-vrfs)
7. [Networks](#-networks)
8. [Interfaces](#-interfaces)
9. [vPC Peers](#-vpc-peers)
10. [Topology](#-topology)
11. [Underlay](#-underlay)
12. [Overlay Extensions](#-overlay-extensions)
13. [Policies](#-policies)
14. [Route Control](#-route-control)
15. [Global Config](#-global-config)
16. [Bulk Import (Excel/CSV)](#-bulk-import-excelcsv)
17. [YAML Deploy](#-yaml-deploy)
18. [Error Reference](#-error-reference)

---

## 🔐 Authentication

All endpoints (except `/health`) require an API key.

| Header | Value | Required |
|---|---|---|
| `X-API-Key` | Your API key string | ✅ Yes |

### Example

```bash
curl -H "X-API-Key: your-api-key" http://<host>:8000/api/v1/fabrics
```

### Unauthorized Response `401`

```json
{
  "detail": "Invalid or missing API key"
}
```

> **Env variable:** Set `NDFC_SOT_API_KEYS` (comma-separated for multiple keys)

---

## 📋 Common Patterns

### Pagination

All list endpoints support pagination:

| Parameter | Type | Default | Max | Description |
|---|---|---|---|---|
| `skip` | integer | `0` | — | Records to skip |
| `limit` | integer | `100` | `1000` | Max records to return |

```bash
GET /api/v1/<resource>?skip=0&limit=50
```

### Standard Response Codes

| Code | Meaning |
|---|---|
| `200` | ✅ Success |
| `201` | ✅ Created |
| `204` | ✅ Deleted (no content) |
| `400` | ❌ Bad Request / Business logic error |
| `401` | 🔒 Unauthorized |
| `404` | ❌ Not Found |
| `409` | ❌ Conflict (duplicate) |
| `422` | ❌ Validation Error |
| `500` | 💥 Server Error |

### Validation Error Response `422`

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

### Referential Integrity

The API validates foreign key references automatically:
- `fabric_id` must reference an existing Fabric
- `switch_id` must reference an existing Switch
- `vrf_id` must reference an existing VRF
- `network_id` must reference an existing Network
- VLANs and VNIs are checked for uniqueness within a fabric

---

## ❤️ Health Check

### `GET /health`

> ⚠️ **No authentication required**

```bash
curl http://<host>:8000/health
```

#### Response `200`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

---

## 🏭 Fabrics

A **Fabric** represents a VXLAN EVPN fabric managed by NDFC.

**Base path:** `/api/v1/fabrics`

---

### `GET /api/v1/fabrics`

List all fabrics.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | ❌ | Pagination offset (default: 0) |
| `limit` | integer | ❌ | Max results (default: 100) |

#### Request

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/fabrics"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "name": "DC1_Fabric",
    "fabric_type": "VXLAN_EVPN",
    "bgp_as": 65001,
    "description": "Data Center 1 Production Fabric",
    "replication_mode": "multicast",
    "anycast_gateway_mac": "2020.0000.00aa",
    "nve_id": 1,
    "enable_nxapi": true,
    "grfield_debug": false,
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `GET /api/v1/fabrics/{fabric_id}`

Get a single fabric.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ✅ | Unique fabric ID |

#### Request

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/fabrics/1"
```

#### Response `200`

```json
{
  "id": 1,
  "name": "DC1_Fabric",
  "fabric_type": "VXLAN_EVPN",
  "bgp_as": 65001,
  "description": "Data Center 1 Production Fabric",
  "replication_mode": "multicast",
  "anycast_gateway_mac": "2020.0000.00aa",
  "nve_id": 1,
  "enable_nxapi": true,
  "grfield_debug": false,
  "created_at": "2026-03-15T10:30:00Z",
  "updated_at": "2026-03-15T10:30:00Z"
}
```

#### Response `404`

```json
{
  "detail": "Fabric 1 not found"
}
```

---

### `POST /api/v1/fabrics`

Create a new fabric.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `name` | string | ✅ | 1–100 chars, **unique** | Fabric name |
| `fabric_type` | string | ✅ | Enum: `VXLAN_EVPN`, `VXLAN_EVPN_MSD`, `LAN_Classic`, `External`, `LAN` | Fabric type |
| `bgp_as` | integer | ✅ | `1`–`4294967295` | BGP AS number |
| `description` | string | ❌ | Max 500 chars | Description |
| `replication_mode` | string | ❌ | Enum: `multicast`, `ingress` | Default: `multicast` |
| `anycast_gateway_mac` | string | ❌ | MAC format `xxxx.xxxx.xxxx` | Anycast GW MAC |
| `nve_id` | integer | ❌ | `1`–`4096` | NVE interface ID (default: 1) |
| `enable_nxapi` | boolean | ❌ | — | Enable NX-API (default: true) |
| `grfield_debug` | boolean | ❌ | — | Enable GR debug (default: false) |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DC2_Fabric",
    "fabric_type": "VXLAN_EVPN",
    "bgp_as": 65002,
    "replication_mode": "multicast",
    "anycast_gateway_mac": "2020.0000.00aa",
    "description": "Data Center 2 Fabric"
  }' \
  "http://<host>:8000/api/v1/fabrics"
```

#### Response `201`

```json
{
  "id": 2,
  "name": "DC2_Fabric",
  "fabric_type": "VXLAN_EVPN",
  "bgp_as": 65002,
  "description": "Data Center 2 Fabric",
  "replication_mode": "multicast",
  "anycast_gateway_mac": "2020.0000.00aa",
  "nve_id": 1,
  "enable_nxapi": true,
  "grfield_debug": false,
  "created_at": "2026-03-30T10:00:00Z",
  "updated_at": "2026-03-30T10:00:00Z"
}
```

#### Response `409`

```json
{
  "detail": "Fabric 'DC2_Fabric' already exists"
}
```

---

### `PUT /api/v1/fabrics/{fabric_id}`

Update an existing fabric (partial update supported).

#### Request

```bash
curl -X PUT \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated DC2 Fabric",
    "replication_mode": "ingress"
  }' \
  "http://<host>:8000/api/v1/fabrics/2"
```

#### Response `200`

*(Returns the updated fabric object)*

---

### `DELETE /api/v1/fabrics/{fabric_id}`

Delete a fabric.

> ⚠️ **Cascade:** Deletes all associated switches, VRFs, networks, interfaces, etc.

```bash
curl -X DELETE -H "X-API-Key: your-key" "http://<host>:8000/api/v1/fabrics/2"
```

#### Response `204` — No Content

#### Response `404`

```json
{
  "detail": "Fabric 2 not found"
}
```

---

## 🔌 Switches (Inventory)

A **Switch** represents a Nexus device managed by NDFC.

**Base path:** `/api/v1/switches`

---

### `GET /api/v1/switches`

List all switches.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | ❌ | Pagination offset |
| `limit` | integer | ❌ | Max results |
| `fabric_id` | integer | ❌ | Filter by fabric |
| `role` | string | ❌ | Filter by role |

#### Request

```bash
curl -H "X-API-Key: your-key" \
  "http://<host>:8000/api/v1/switches?fabric_id=1&role=leaf"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "name": "DC1-Leaf-01",
    "fabric_id": 1,
    "serial_number": "SAL12345ABC",
    "model": "N9K-C93180YC-FX",
    "role": "leaf",
    "mgmt_ip": "10.0.0.11",
    "vtep_ip": "10.1.1.11",
    "loopback0_ip": "10.2.0.11/32",
    "loopback1_ip": "10.2.1.11/32",
    "system_mac": "00:11:22:33:44:55",
    "software_version": "10.3(2)",
    "vpc_id": null,
    "vpc_peer_id": null,
    "description": "Leaf switch Pod1",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `GET /api/v1/switches/{switch_id}`

Get a single switch.

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/switches/1"
```

---

### `POST /api/v1/switches`

Create a new switch.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `name` | string | ✅ | 1–255 chars, **unique** | Switch hostname |
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `serial_number` | string | ✅ | **Unique** | Device serial number |
| `model` | string | ❌ | Max 100 chars | Hardware model (e.g., `N9K-C93180YC-FX`) |
| `role` | string | ✅ | Enum: `spine`, `leaf`, `border`, `border_gateway`, `super_spine`, `border_spine`, `border_gateway_spine`, `access` | Switch role in fabric |
| `mgmt_ip` | string | ✅ | Valid IPv4 | Management IP address |
| `vtep_ip` | string | ❌ | Valid IPv4 | VTEP (NVE) source IP |
| `loopback0_ip` | string | ❌ | Valid IPv4 CIDR | Loopback0 IP (routing) |
| `loopback1_ip` | string | ❌ | Valid IPv4 CIDR | Loopback1 IP (VTEP) |
| `system_mac` | string | ❌ | MAC format | System MAC address |
| `software_version` | string | ❌ | Max 50 chars | NX-OS version |
| `vpc_id` | integer | ❌ | — | vPC domain ID |
| `vpc_peer_id` | integer | ❌ | Must exist | vPC peer switch ID |
| `description` | string | ❌ | Max 500 chars | Description |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DC1-Spine-01",
    "fabric_id": 1,
    "serial_number": "SAL67890DEF",
    "model": "N9K-C9364C-GX",
    "role": "spine",
    "mgmt_ip": "10.0.0.1",
    "loopback0_ip": "10.2.0.1/32",
    "software_version": "10.3(2)"
  }' \
  "http://<host>:8000/api/v1/switches"
```

#### Response `201`

```json
{
  "id": 2,
  "name": "DC1-Spine-01",
  "fabric_id": 1,
  "serial_number": "SAL67890DEF",
  "model": "N9K-C9364C-GX",
  "role": "spine",
  "mgmt_ip": "10.0.0.1",
  "vtep_ip": null,
  "loopback0_ip": "10.2.0.1/32",
  "loopback1_ip": null,
  "system_mac": null,
  "software_version": "10.3(2)",
  "vpc_id": null,
  "vpc_peer_id": null,
  "description": null,
  "created_at": "2026-03-30T10:00:00Z",
  "updated_at": "2026-03-30T10:00:00Z"
}
```

#### Validation Errors

| Scenario | Code | Message |
|---|---|---|
| `fabric_id` doesn't exist | `400` | `Fabric 99 does not exist` |
| Duplicate `serial_number` | `409` | `Switch with serial 'X' already exists` |
| Duplicate `name` | `409` | `Switch 'X' already exists` |
| Invalid `role` | `422` | `Input should be 'spine', 'leaf', ...` |

---

### `PUT /api/v1/switches/{switch_id}`

Update a switch.

```bash
curl -X PUT \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"software_version": "10.4(1)", "description": "Upgraded"}' \
  "http://<host>:8000/api/v1/switches/2"
```

---

### `DELETE /api/v1/switches/{switch_id}`

Delete a switch.

> ⚠️ **Cascade:** Deletes all associated interfaces.

```bash
curl -X DELETE -H "X-API-Key: your-key" "http://<host>:8000/api/v1/switches/2"
```

---

## 🔀 VRFs

A **VRF** (Virtual Routing and Forwarding) belongs to a fabric.

**Base path:** `/api/v1/vrfs`

---

### `GET /api/v1/vrfs`

List all VRFs.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | ❌ | Pagination offset |
| `limit` | integer | ❌ | Max results |
| `fabric_id` | integer | ❌ | Filter by fabric |

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/vrfs?fabric_id=1"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "name": "VRF_Production",
    "fabric_id": 1,
    "vrf_id": 50001,
    "vlan_id": 2001,
    "vrf_template": "Default_VRF_Universal",
    "vrf_extension_template": "Default_VRF_Extension_Universal",
    "route_target_import": "50001:50001",
    "route_target_export": "50001:50001",
    "route_target_import_evpn": "50001:50001",
    "route_target_export_evpn": "50001:50001",
    "ipv6_link_local": false,
    "max_bgp_paths": 1,
    "max_ibgp_paths": 2,
    "adv_default_route": true,
    "redistribute_direct": true,
    "attach_switches": [1, 3, 5],
    "description": "Production VRF",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `GET /api/v1/vrfs/{vrf_id}`

Get a single VRF.

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/vrfs/1"
```

---

### `POST /api/v1/vrfs`

Create a new VRF.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `name` | string | ✅ | 1–100 chars, **unique per fabric** | VRF name |
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `vrf_id` | integer | ✅ | `1`–`16777215`, **unique per fabric** | VRF VNI segment ID |
| `vlan_id` | integer | ✅ | `2`–`4094`, **unique per fabric** | SVI VLAN for the VRF |
| `vrf_template` | string | ❌ | Max 255 chars | VRF template (default: `Default_VRF_Universal`) |
| `vrf_extension_template` | string | ❌ | Max 255 chars | VRF extension template |
| `route_target_import` | string | ❌ | RT format `ASN:VNI` | Import route target |
| `route_target_export` | string | ❌ | RT format `ASN:VNI` | Export route target |
| `route_target_import_evpn` | string | ❌ | RT format | EVPN import RT |
| `route_target_export_evpn` | string | ❌ | RT format | EVPN export RT |
| `ipv6_link_local` | boolean | ❌ | — | Enable IPv6 link-local |
| `max_bgp_paths` | integer | ❌ | `1`–`64` | Max BGP paths |
| `max_ibgp_paths` | integer | ❌ | `1`–`64` | Max iBGP paths |
| `adv_default_route` | boolean | ❌ | — | Advertise default route |
| `redistribute_direct` | boolean | ❌ | — | Redistribute directly connected |
| `attach_switches` | list[int] | ❌ | Each must exist in fabric | Switch IDs to attach VRF |
| `description` | string | ❌ | Max 500 chars | Description |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VRF_DMZ",
    "fabric_id": 1,
    "vrf_id": 50002,
    "vlan_id": 2002,
    "vrf_template": "Default_VRF_Universal",
    "route_target_import": "50002:50002",
    "route_target_export": "50002:50002",
    "attach_switches": [1, 3],
    "description": "DMZ VRF"
  }' \
  "http://<host>:8000/api/v1/vrfs"
```

#### Response `201`

```json
{
  "id": 2,
  "name": "VRF_DMZ",
  "fabric_id": 1,
  "vrf_id": 50002,
  "vlan_id": 2002,
  "vrf_template": "Default_VRF_Universal",
  "vrf_extension_template": null,
  "route_target_import": "50002:50002",
  "route_target_export": "50002:50002",
  "route_target_import_evpn": null,
  "route_target_export_evpn": null,
  "ipv6_link_local": false,
  "max_bgp_paths": 1,
  "max_ibgp_paths": 2,
  "adv_default_route": true,
  "redistribute_direct": true,
  "attach_switches": [1, 3],
  "description": "DMZ VRF",
  "created_at": "2026-03-30T10:00:00Z",
  "updated_at": "2026-03-30T10:00:00Z"
}
```

#### Validation Errors

| Scenario | Code | Message |
|---|---|---|
| `fabric_id` doesn't exist | `400` | `Fabric 99 does not exist` |
| Duplicate `vrf_id` in fabric | `409` | `VRF VNI 50002 already used in fabric 1` |
| Duplicate `vlan_id` in fabric | `409` | `VLAN 2002 already used in fabric 1` |
| Duplicate `name` in fabric | `409` | `VRF 'VRF_DMZ' already exists in fabric 1` |
| `vlan_id` < 2 or > 4094 | `422` | `Input should be >= 2 and <= 4094` |
| `vrf_id` > 16777215 | `422` | `Input should be <= 16777215` |
| `attach_switches` switch not in fabric | `400` | `Switch 99 does not belong to fabric 1` |

---

### `PUT /api/v1/vrfs/{vrf_id}`

Update a VRF. All fields are optional.

```bash
curl -X PUT \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"attach_switches": [1, 3, 5], "description": "Updated DMZ"}' \
  "http://<host>:8000/api/v1/vrfs/2"
```

---

### `DELETE /api/v1/vrfs/{vrf_id}`

Delete a VRF.

> ⚠️ **Cascade:** Deletes all associated networks.

```bash
curl -X DELETE -H "X-API-Key: your-key" "http://<host>:8000/api/v1/vrfs/2"
```

---

## 🌐 Networks

A **Network** represents a VXLAN L2/L3 segment.

**Base path:** `/api/v1/networks`

---

### `GET /api/v1/networks`

List all networks.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | ❌ | Pagination offset |
| `limit` | integer | ❌ | Max results |
| `fabric_id` | integer | ❌ | Filter by fabric |
| `vrf_id` | integer | ❌ | Filter by VRF |

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/networks?fabric_id=1"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "name": "Net_Web_Tier",
    "fabric_id": 1,
    "vrf_id": 1,
    "network_id": 30001,
    "vlan_id": 100,
    "vlan_name": "Web_Tier",
    "gateway_ip": "10.1.100.1/24",
    "gateway_ipv6": null,
    "is_layer2_only": false,
    "mtu": 9216,
    "arp_suppress": true,
    "ir_enable": false,
    "mcast_group": "239.1.1.1",
    "dhcp_server_1": null,
    "dhcp_server_vrf": null,
    "trm_enable": false,
    "route_target_both": true,
    "network_template": "Default_Network_Universal",
    "network_extension_template": "Default_Network_Extension_Universal",
    "attach_switches": [
      {"switch_id": 1, "ports": ["Ethernet1/10", "Ethernet1/11"]},
      {"switch_id": 3, "ports": ["Ethernet1/10"]}
    ],
    "description": "Web Tier Network",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `GET /api/v1/networks/{network_id}`

Get a single network.

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/networks/1"
```

---

### `POST /api/v1/networks`

Create a new network.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `name` | string | ✅ | 1–100 chars, **unique per fabric** | Network name |
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `vrf_id` | integer | ❌ | Must exist in same fabric | VRF (null = L2 only) |
| `network_id` | integer | ✅ | `1`–`16777215`, **unique per fabric** | Network VNI segment ID |
| `vlan_id` | integer | ✅ | `2`–`4094`, **unique per fabric** | VLAN ID |
| `vlan_name` | string | ❌ | Max 32 chars | VLAN name |
| `gateway_ip` | string | ❌ | Valid IPv4 CIDR (e.g., `10.1.1.1/24`) | Gateway IP for SVI |
| `gateway_ipv6` | string | ❌ | Valid IPv6 CIDR | IPv6 gateway |
| `is_layer2_only` | boolean | ❌ | — | L2-only network (default: false) |
| `mtu` | integer | ❌ | `576`–`9216` | MTU (default: 9216) |
| `arp_suppress` | boolean | ❌ | — | Enable ARP suppression |
| `ir_enable` | boolean | ❌ | — | Enable ingress replication |
| `mcast_group` | string | ❌ | Valid multicast IP | Multicast group address |
| `dhcp_server_1` | string | ❌ | Valid IPv4 | DHCP relay server IP |
| `dhcp_server_vrf` | string | ❌ | — | VRF for DHCP relay |
| `trm_enable` | boolean | ❌ | — | Enable TRM |
| `route_target_both` | boolean | ❌ | — | Use both import/export RT |
| `network_template` | string | ❌ | Max 255 chars | Network template |
| `network_extension_template` | string | ❌ | Max 255 chars | Extension template |
| `attach_switches` | list[object] | ❌ | See below | Switch attachments with ports |
| `description` | string | ❌ | Max 500 chars | Description |

#### Switch Attachment Object

| Field | Type | Required | Description |
|---|---|---|---|
| `switch_id` | integer | ✅ | Switch ID (must exist in same fabric) |
| `ports` | list[string] | ❌ | Ports to attach (e.g., `["Ethernet1/10"]`) |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Net_App_Tier",
    "fabric_id": 1,
    "vrf_id": 1,
    "network_id": 30002,
    "vlan_id": 101,
    "vlan_name": "App_Tier",
    "gateway_ip": "10.1.101.1/24",
    "is_layer2_only": false,
    "mtu": 9216,
    "arp_suppress": true,
    "attach_switches": [
      {"switch_id": 1, "ports": ["Ethernet1/12"]},
      {"switch_id": 3, "ports": ["Ethernet1/12", "Ethernet1/13"]}
    ],
    "description": "Application Tier Network"
  }' \
  "http://<host>:8000/api/v1/networks"
```

#### Validation Errors

| Scenario | Code | Message |
|---|---|---|
| `fabric_id` doesn't exist | `400` | `Fabric 99 does not exist` |
| `vrf_id` not in same fabric | `400` | `VRF 1 does not belong to fabric 2` |
| Duplicate `network_id` in fabric | `409` | `Network VNI 30002 already used in fabric 1` |
| Duplicate `vlan_id` in fabric | `409` | `VLAN 101 already used in fabric 1` |
| L3 network without `gateway_ip` | `400` | `gateway_ip required when is_layer2_only is false` |
| Invalid `gateway_ip` format | `422` | `Invalid IPv4 CIDR format` |
| `mtu` out of range | `422` | `Input should be >= 576 and <= 9216` |
| `attach_switches` switch not in fabric | `400` | `Switch 99 does not belong to fabric 1` |

---

### `PUT /api/v1/networks/{network_id}`

Update a network.

```bash
curl -X PUT \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_ip": "10.1.101.254/24",
    "attach_switches": [
      {"switch_id": 1, "ports": ["Ethernet1/12", "Ethernet1/13"]}
    ]
  }' \
  "http://<host>:8000/api/v1/networks/2"
```

---

### `DELETE /api/v1/networks/{network_id}`

Delete a network.

```bash
curl -X DELETE -H "X-API-Key: your-key" "http://<host>:8000/api/v1/networks/2"
```

---

## 🔗 Interfaces

An **Interface** represents a physical or logical port on a switch.

**Base path:** `/api/v1/interfaces`

---

### `GET /api/v1/interfaces`

List all interfaces.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | ❌ | Pagination offset |
| `limit` | integer | ❌ | Max results |
| `switch_id` | integer | ❌ | Filter by switch |
| `fabric_id` | integer | ❌ | Filter by fabric |
| `interface_type` | string | ❌ | Filter: `routed`, `trunk`, `access`, `loopback`, `port_channel`, `vpc`, `subinterface`, `svi`, `nve`, `mgmt` |

```bash
curl -H "X-API-Key: your-key" \
  "http://<host>:8000/api/v1/interfaces?switch_id=1&interface_type=trunk"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "name": "Ethernet1/1",
    "switch_id": 1,
    "fabric_id": 1,
    "interface_type": "trunk",
    "mode": "trunk",
    "mtu": 9216,
    "speed": "auto",
    "admin_state": "up",
    "access_vlan": null,
    "trunk_allowed_vlans": "100-110,200-210",
    "native_vlan": 1,
    "ip_address": null,
    "ipv6_address": null,
    "vrf": null,
    "description": "Uplink to Spine-1",
    "po_id": null,
    "members": null,
    "fex_id": null,
    "bpdu_guard": false,
    "port_fast": false,
    "orphan_port": false,
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `GET /api/v1/interfaces/{interface_id}`

Get a single interface.

---

### `POST /api/v1/interfaces`

Create a new interface.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `name` | string | ✅ | **Unique per switch** | Interface name (e.g., `Ethernet1/1`) |
| `switch_id` | integer | ✅ | Must exist | Associated switch |
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `interface_type` | string | ✅ | Enum: `routed`, `trunk`, `access`, `loopback`, `port_channel`, `vpc`, `subinterface`, `svi`, `nve`, `mgmt` | Interface type |
| `mode` | string | ❌ | Enum: `trunk`, `access`, `routed`, `monitor`, `fabricpath` | Switchport mode |
| `mtu` | integer | ❌ | `576`–`9216` | MTU size |
| `speed` | string | ❌ | `auto`, `100M`, `1G`, `10G`, `25G`, `40G`, `100G`, `400G` | Speed |
| `admin_state` | string | ❌ | Enum: `up`, `down` | Admin state (default: `up`) |
| `access_vlan` | integer | ❌ | `1`–`4094` | Access VLAN (for access mode) |
| `trunk_allowed_vlans` | string | ❌ | VLAN range (e.g., `100-110,200`) | Trunk allowed VLANs |
| `native_vlan` | integer | ❌ | `1`–`4094` | Native VLAN for trunk |
| `ip_address` | string | ❌ | Valid IPv4 CIDR | IP address (routed/loopback/SVI) |
| `ipv6_address` | string | ❌ | Valid IPv6 CIDR | IPv6 address |
| `vrf` | string | ❌ | — | VRF membership for routed interface |
| `po_id` | integer | ❌ | — | Port-channel ID (for member ports) |
| `members` | list[string] | ❌ | — | Member interfaces (for port-channel/vPC) |
| `fex_id` | integer | ❌ | `100`–`199` | FEX ID (for FEX HIF ports) |
| `bpdu_guard` | boolean | ❌ | — | Enable BPDU Guard |
| `port_fast` | boolean | ❌ | — | Enable PortFast |
| `orphan_port` | boolean | ❌ | — | vPC orphan port |
| `description` | string | ❌ | Max 500 chars | Description |

#### Request — Trunk Interface

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ethernet1/3",
    "switch_id": 1,
    "fabric_id": 1,
    "interface_type": "trunk",
    "mode": "trunk",
    "mtu": 9216,
    "trunk_allowed_vlans": "100-110",
    "native_vlan": 1,
    "admin_state": "up",
    "description": "Server trunk port"
  }' \
  "http://<host>:8000/api/v1/interfaces"
```

#### Request — Routed Interface

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ethernet1/48",
    "switch_id": 1,
    "fabric_id": 1,
    "interface_type": "routed",
    "mode": "routed",
    "ip_address": "10.10.1.1/30",
    "vrf": "VRF_Production",
    "mtu": 9216,
    "admin_state": "up",
    "description": "P2P link to border"
  }' \
  "http://<host>:8000/api/v1/interfaces"
```

#### Request — Port-Channel

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "port-channel10",
    "switch_id": 1,
    "fabric_id": 1,
    "interface_type": "port_channel",
    "mode": "trunk",
    "trunk_allowed_vlans": "100-110",
    "members": ["Ethernet1/5", "Ethernet1/6"],
    "mtu": 9216,
    "admin_state": "up",
    "description": "Server bundle"
  }' \
  "http://<host>:8000/api/v1/interfaces"
```

#### Validation Errors

| Scenario | Code | Message |
|---|---|---|
| Duplicate interface name on switch | `409` | `Interface 'Ethernet1/3' already exists on switch 1` |
| `switch_id` doesn't exist | `400` | `Switch 99 does not exist` |
| `access` mode without `access_vlan` | `400` | `access_vlan required for access interfaces` |
| `trunk` mode without `trunk_allowed_vlans` | `400` | `trunk_allowed_vlans required for trunk interfaces` |
| `routed` mode without `ip_address` | `400` | `ip_address required for routed interfaces` |
| `mtu` out of range | `422` | `Input should be >= 576 and <= 9216` |

---

### `PUT /api/v1/interfaces/{interface_id}`

Update an interface.

### `DELETE /api/v1/interfaces/{interface_id}`

Delete an interface.

---

## 🤝 vPC Peers

A **vPC Peer** defines the virtual Port Channel domain between two switches.

**Base path:** `/api/v1/vpc-peers`

---

### `GET /api/v1/vpc-peers`

List all vPC peer links.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ❌ | Filter by fabric |

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/vpc-peers?fabric_id=1"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "fabric_id": 1,
    "switch1_id": 1,
    "switch2_id": 2,
    "vpc_domain_id": 100,
    "peer_keepalive_src": "10.0.0.11",
    "peer_keepalive_dst": "10.0.0.12",
    "peer_keepalive_vrf": "management",
    "virtual_peer_ip": null,
    "virtual_peer_ipv6": null,
    "peer_link_port_channel": 1,
    "peer_link_members": ["Ethernet1/53", "Ethernet1/54"],
    "delay_restore": 150,
    "auto_recovery": true,
    "description": "vPC between Leaf-01 and Leaf-02",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `GET /api/v1/vpc-peers/{vpc_peer_id}`

Get a single vPC peer.

---

### `POST /api/v1/vpc-peers`

Create a new vPC peer link.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `switch1_id` | integer | ✅ | Must exist in fabric | First switch |
| `switch2_id` | integer | ✅ | Must exist in fabric, ≠ switch1_id | Second switch |
| `vpc_domain_id` | integer | ✅ | `1`–`1000`, **unique per fabric** | vPC domain ID |
| `peer_keepalive_src` | string | ✅ | Valid IPv4 | Peer keepalive source IP |
| `peer_keepalive_dst` | string | ✅ | Valid IPv4 | Peer keepalive destination IP |
| `peer_keepalive_vrf` | string | ❌ | — | VRF for keepalive (default: `management`) |
| `virtual_peer_ip` | string | ❌ | Valid IPv4 | Virtual peer link IP |
| `virtual_peer_ipv6` | string | ❌ | Valid IPv6 | Virtual peer link IPv6 |
| `peer_link_port_channel` | integer | ❌ | `1`–`4096` | Port-channel ID for peer link |
| `peer_link_members` | list[string] | ❌ | — | Physical members of peer link |
| `delay_restore` | integer | ❌ | `1`–`3600` | Delay restore timer (seconds) |
| `auto_recovery` | boolean | ❌ | — | Enable auto-recovery |
| `description` | string | ❌ | Max 500 chars | Description |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fabric_id": 1,
    "switch1_id": 1,
    "switch2_id": 2,
    "vpc_domain_id": 100,
    "peer_keepalive_src": "10.0.0.11",
    "peer_keepalive_dst": "10.0.0.12",
    "peer_keepalive_vrf": "management",
    "peer_link_port_channel": 1,
    "peer_link_members": ["Ethernet1/53", "Ethernet1/54"],
    "delay_restore": 150,
    "auto_recovery": true
  }' \
  "http://<host>:8000/api/v1/vpc-peers"
```

#### Validation Errors

| Scenario | Code | Message |
|---|---|---|
| `switch1_id` == `switch2_id` | `400` | `vPC peer switches must be different` |
| Switch not in fabric | `400` | `Switch 1 does not belong to fabric 2` |
| Duplicate domain ID | `409` | `vPC domain 100 already exists in fabric 1` |
| Switch already in vPC pair | `409` | `Switch 1 already has a vPC peer in fabric 1` |

---

### `PUT /api/v1/vpc-peers/{vpc_peer_id}`

Update a vPC peer.

### `DELETE /api/v1/vpc-peers/{vpc_peer_id}`

Delete a vPC peer.

---

## 🗺️ Topology

Manage fabric topology — links between switches.

**Base path:** `/api/v1/topology`

---

### `GET /api/v1/topology`

List all topology links.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ❌ | Filter by fabric |

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/topology?fabric_id=1"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "fabric_id": 1,
    "source_switch_id": 1,
    "source_interface": "Ethernet1/49",
    "dest_switch_id": 5,
    "dest_interface": "Ethernet1/1",
    "link_type": "fabric",
    "mtu": 9216,
    "description": "Leaf-01 to Spine-01",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `POST /api/v1/topology`

Create a topology link.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `source_switch_id` | integer | ✅ | Must exist in fabric | Source switch |
| `source_interface` | string | ✅ | — | Source interface name |
| `dest_switch_id` | integer | ✅ | Must exist in fabric | Destination switch |
| `dest_interface` | string | ✅ | — | Destination interface name |
| `link_type` | string | ❌ | Enum: `fabric`, `vpc_peer_link`, `inter_fabric`, `external` | Link type (default: `fabric`) |
| `mtu` | integer | ❌ | `576`–`9216` | Link MTU |
| `description` | string | ❌ | Max 500 chars | Description |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fabric_id": 1,
    "source_switch_id": 1,
    "source_interface": "Ethernet1/49",
    "dest_switch_id": 5,
    "dest_interface": "Ethernet1/1",
    "link_type": "fabric",
    "mtu": 9216,
    "description": "Leaf-01 to Spine-01"
  }' \
  "http://<host>:8000/api/v1/topology"
```

---

### `PUT /api/v1/topology/{link_id}`

Update a topology link.

### `DELETE /api/v1/topology/{link_id}`

Delete a topology link.

---

## 🔧 Underlay

Manage underlay protocol configuration (OSPF, IS-IS, PIM, BFD, etc.).

**Base path:** `/api/v1/underlay`

---

### `GET /api/v1/underlay`

List all underlay configurations.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ❌ | Filter by fabric |

```bash
curl -H "X-API-Key: your-key" "http://<host>:8000/api/v1/underlay?fabric_id=1"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "fabric_id": 1,
    "routing_protocol": "ospf",
    "ospf_area": "0.0.0.0",
    "ospf_process_tag": "UNDERLAY",
    "isis_level": null,
    "isis_net_id": null,
    "bgp_auth_enable": false,
    "bgp_auth_key": null,
    "ospf_auth_enable": false,
    "ospf_auth_key": null,
    "pim_rp_address": "10.254.254.1",
    "pim_rp_loopback_id": 250,
    "is_anycast_rp": true,
    "bfd_enable": true,
    "bfd_interval": 50,
    "bfd_min_rx": 50,
    "bfd_multiplier": 3,
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `POST /api/v1/underlay`

Create underlay configuration.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `fabric_id` | integer | ✅ | Must exist, **one per fabric** | Associated fabric |
| `routing_protocol` | string | ✅ | Enum: `ospf`, `is_is` | Underlay routing protocol |
| `ospf_area` | string | ❌ | Valid area ID (e.g., `0.0.0.0`) | OSPF area (when `ospf`) |
| `ospf_process_tag` | string | ❌ | Max 20 chars | OSPF process tag |
| `isis_level` | string | ❌ | Enum: `level-1`, `level-2`, `level-1-2` | IS-IS level |
| `isis_net_id` | string | ❌ | Valid NET ID | IS-IS NET ID |
| `bgp_auth_enable` | boolean | ❌ | — | Enable BGP authentication |
| `bgp_auth_key` | string | ❌ | — | BGP auth key (encrypted) |
| `ospf_auth_enable` | boolean | ❌ | — | Enable OSPF authentication |
| `ospf_auth_key` | string | ❌ | — | OSPF auth key |
| `pim_rp_address` | string | ❌ | Valid IPv4 | PIM RP address |
| `pim_rp_loopback_id` | integer | ❌ | `0`–`1023` | Loopback for RP |
| `is_anycast_rp` | boolean | ❌ | — | Anycast RP enable |
| `bfd_enable` | boolean | ❌ | — | Enable BFD |
| `bfd_interval` | integer | ❌ | `50`–`999` | BFD interval (ms) |
| `bfd_min_rx` | integer | ❌ | `50`–`999` | BFD minimum RX (ms) |
| `bfd_multiplier` | integer | ❌ | `1`–`50` | BFD detect multiplier |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fabric_id": 1,
    "routing_protocol": "ospf",
    "ospf_area": "0.0.0.0",
    "ospf_process_tag": "UNDERLAY",
    "pim_rp_address": "10.254.254.1",
    "pim_rp_loopback_id": 250,
    "is_anycast_rp": true,
    "bfd_enable": true,
    "bfd_interval": 50,
    "bfd_min_rx": 50,
    "bfd_multiplier": 3
  }' \
  "http://<host>:8000/api/v1/underlay"
```

#### Validation Errors

| Scenario | Code | Message |
|---|---|---|
| Fabric already has underlay config | `409` | `Underlay config already exists for fabric 1` |
| `routing_protocol=ospf` but no `ospf_area` | `400` | `ospf_area required when routing_protocol is ospf` |
| `routing_protocol=is_is` but no `isis_level` | `400` | `isis_level required when routing_protocol is is_is` |

---

### `PUT /api/v1/underlay/{underlay_id}`

Update underlay configuration.

### `DELETE /api/v1/underlay/{underlay_id}`

Delete underlay configuration.

---

## 🔄 Overlay Extensions

Manage overlay extension configurations (multisite, DCI, etc.).

**Base path:** `/api/v1/overlay-extensions`

---

### `GET /api/v1/overlay-extensions`

List all overlay extensions.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ❌ | Filter by fabric |

```bash
curl -H "X-API-Key: your-key" \
  "http://<host>:8000/api/v1/overlay-extensions?fabric_id=1"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "fabric_id": 1,
    "extension_type": "multisite",
    "source_fabric_id": 1,
    "dest_fabric_id": 2,
    "vrf_id": 1,
    "network_id": null,
    "multisite_bgw_ip": "10.100.0.1",
    "dci_links": [
      {"src_interface": "Ethernet1/49", "dst_interface": "Ethernet1/49"}
    ],
    "description": "DCI to DC2",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `POST /api/v1/overlay-extensions`

Create an overlay extension.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `extension_type` | string | ✅ | Enum: `multisite`, `vrf_lite`, `mpls_handoff`, `ext_fabric` | Extension type |
| `source_fabric_id` | integer | ✅ | Must exist | Source fabric |
| `dest_fabric_id` | integer | ❌ | Must exist | Destination fabric |
| `vrf_id` | integer | ❌ | Must exist | VRF to extend |
| `network_id` | integer | ❌ | Must exist | Network to extend |
| `multisite_bgw_ip` | string | ❌ | Valid IPv4 | Border Gateway IP |
| `dci_links` | list[object] | ❌ | — | DCI link definitions |
| `description` | string | ❌ | Max 500 chars | Description |

---

### `PUT /api/v1/overlay-extensions/{extension_id}`

Update an overlay extension.

### `DELETE /api/v1/overlay-extensions/{extension_id}`

Delete an overlay extension.

---

## 📜 Policies

Manage NDFC policies applied to switches.

**Base path:** `/api/v1/policies`

---

### `GET /api/v1/policies`

List all policies.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ❌ | Filter by fabric |
| `switch_id` | integer | ❌ | Filter by switch |
| `policy_type` | string | ❌ | Filter by type |

```bash
curl -H "X-API-Key: your-key" \
  "http://<host>:8000/api/v1/policies?fabric_id=1&policy_type=SWITCH_FREEFORM"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "fabric_id": 1,
    "switch_id": 1,
    "policy_type": "SWITCH_FREEFORM",
    "template_name": "switch_freeform",
    "priority": 500,
    "config_content": "interface loopback99\n  ip address 1.1.1.1/32",
    "description": "Custom loopback for monitoring",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `POST /api/v1/policies`

Create a policy.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `switch_id` | integer | ✅ | Must exist in fabric | Target switch |
| `policy_type` | string | ✅ | Enum: `SWITCH_FREEFORM`, `INTERFACE_FREEFORM`, `VRF_FREEFORM`, `NETWORK_FREEFORM`, `CUSTOM_TEMPLATE` | Policy type |
| `template_name` | string | ✅ | Max 255 chars | NDFC template name |
| `priority` | integer | ❌ | `1`–`1000` | Policy priority (default: 500) |
| `config_content` | string | ❌ | — | Freeform config / template vars |
| `description` | string | ❌ | Max 500 chars | Description |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fabric_id": 1,
    "switch_id": 1,
    "policy_type": "SWITCH_FREEFORM",
    "template_name": "switch_freeform",
    "priority": 500,
    "config_content": "interface loopback99\n  ip address 1.1.1.1/32",
    "description": "Monitoring loopback"
  }' \
  "http://<host>:8000/api/v1/policies"
```

---

### `PUT /api/v1/policies/{policy_id}`

Update a policy.

### `DELETE /api/v1/policies/{policy_id}`

Delete a policy.

---

## 🛣️ Route Control

Manage route maps, prefix lists, community lists, and static routes.

**Base path:** `/api/v1/route-control`

---

### `GET /api/v1/route-control`

List all route control entries.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ❌ | Filter by fabric |
| `switch_id` | integer | ❌ | Filter by switch |
| `control_type` | string | ❌ | Filter: `route_map`, `prefix_list`, `community_list`, `static_route` |

```bash
curl -H "X-API-Key: your-key" \
  "http://<host>:8000/api/v1/route-control?fabric_id=1&control_type=static_route"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "fabric_id": 1,
    "switch_id": 1,
    "control_type": "static_route",
    "name": "default_route",
    "vrf": "VRF_Production",
    "entries": [
      {
        "prefix": "0.0.0.0/0",
        "next_hop": "10.1.1.1",
        "preference": 1,
        "tag": null
      }
    ],
    "description": "Default route to firewall",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `POST /api/v1/route-control`

Create a route control entry.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `switch_id` | integer | ✅ | Must exist in fabric | Target switch |
| `control_type` | string | ✅ | Enum: `route_map`, `prefix_list`, `community_list`, `static_route` | Type |
| `name` | string | ✅ | 1–100 chars | Name (unique per switch + type) |
| `vrf` | string | ❌ | — | VRF context |
| `entries` | list[object] | ✅ | At least 1 entry | Route entries (see below) |
| `description` | string | ❌ | Max 500 chars | Description |

#### Entry Object — Static Route

| Field | Type | Required | Description |
|---|---|---|---|
| `prefix` | string | ✅ | Destination prefix (e.g., `0.0.0.0/0`) |
| `next_hop` | string | ✅ | Next-hop IP |
| `preference` | integer | ❌ | Admin distance (1–255) |
| `tag` | integer | ❌ | Route tag |

#### Entry Object — Prefix List

| Field | Type | Required | Description |
|---|---|---|---|
| `sequence` | integer | ✅ | Sequence number |
| `action` | string | ✅ | `permit` or `deny` |
| `prefix` | string | ✅ | IP prefix |
| `ge` | integer | ❌ | Greater-than-or-equal mask length |
| `le` | integer | ❌ | Less-than-or-equal mask length |

#### Entry Object — Route Map

| Field | Type | Required | Description |
|---|---|---|---|
| `sequence` | integer | ✅ | Sequence number |
| `action` | string | ✅ | `permit` or `deny` |
| `match_prefix_list` | string | ❌ | Match prefix list name |
| `match_community` | string | ❌ | Match community list name |
| `set_local_pref` | integer | ❌ | Set local preference |
| `set_community` | string | ❌ | Set community |

#### Request — Static Route

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fabric_id": 1,
    "switch_id": 1,
    "control_type": "static_route",
    "name": "default_to_fw",
    "vrf": "VRF_Production",
    "entries": [
      {"prefix": "0.0.0.0/0", "next_hop": "10.1.1.1", "preference": 1}
    ],
    "description": "Default route to firewall"
  }' \
  "http://<host>:8000/api/v1/route-control"
```

---

### `PUT /api/v1/route-control/{route_control_id}`

Update a route control entry.

### `DELETE /api/v1/route-control/{route_control_id}`

Delete a route control entry.

---

## ⚙️ Global Config

Manage global/fabric-wide configuration parameters.

**Base path:** `/api/v1/global-config`

---

### `GET /api/v1/global-config`

List all global config entries.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ❌ | Filter by fabric |

```bash
curl -H "X-API-Key: your-key" \
  "http://<host>:8000/api/v1/global-config?fabric_id=1"
```

#### Response `200`

```json
[
  {
    "id": 1,
    "fabric_id": 1,
    "config_key": "ADVERTISE_PIP_BGP",
    "config_value": "true",
    "config_type": "boolean",
    "description": "Advertise PIP in BGP",
    "created_at": "2026-03-15T10:30:00Z",
    "updated_at": "2026-03-15T10:30:00Z"
  }
]
```

---

### `POST /api/v1/global-config`

Create a global config entry.

#### Request Body

| Field | Type | Required | Validation | Description |
|---|---|---|---|---|
| `fabric_id` | integer | ✅ | Must exist | Associated fabric |
| `config_key` | string | ✅ | **Unique per fabric** | Config parameter name |
| `config_value` | string | ✅ | — | Config value |
| `config_type` | string | ❌ | Enum: `string`, `boolean`, `integer`, `ipv4`, `list` | Value type |
| `description` | string | ❌ | Max 500 chars | Description |

#### Common Config Keys

| Key | Type | Example Value | Description |
|---|---|---|---|
| `ADVERTISE_PIP_BGP` | boolean | `true` | Advertise PIP in BGP |
| `ENABLE_PVLAN` | boolean | `false` | Enable private VLAN |
| `ENABLE_NETFLOW` | boolean | `false` | Enable NetFlow |
| `STRICT_CC_MODE` | boolean | `false` | Strict config compliance |
| `DNS_SERVER_IP_LIST` | list | `8.8.8.8,8.8.4.4` | DNS servers |
| `NTP_SERVER_IP_LIST` | list | `10.0.0.100` | NTP servers |
| `SYSLOG_SERVER_IP_LIST` | list | `10.0.0.101` | Syslog servers |
| `SNMP_SERVER_IP_LIST` | list | `10.0.0.102` | SNMP trap targets |
| `AAA_SERVER_CONF` | string | *(tacacs config)* | AAA server config |
| `BANNER_MOTD` | string | `Authorized access only` | Login banner |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fabric_id": 1,
    "config_key": "DNS_SERVER_IP_LIST",
    "config_value": "8.8.8.8,8.8.4.4",
    "config_type": "list",
    "description": "DNS servers for the fabric"
  }' \
  "http://<host>:8000/api/v1/global-config"
```

---

### `PUT /api/v1/global-config/{config_id}`

Update a global config entry.

### `DELETE /api/v1/global-config/{config_id}`

Delete a global config entry.

---

## 📥 Bulk Import (Excel/CSV)

Import data from Excel or CSV files.

**Base path:** `/api/v1/import`

---

### `POST /api/v1/import/excel`

Bulk import from an Excel file (`.xlsx`).

#### Request

- **Content-Type:** `multipart/form-data`
- **File field:** `file`

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -F "file=@/path/to/data.xlsx" \
  "http://<host>:8000/api/v1/import/excel"
```

#### Expected Excel Format

The Excel file should contain sheets named after resources:

| Sheet Name | Required Columns |
|---|---|
| `fabrics` | `name`, `fabric_type`, `bgp_as` |
| `switches` | `name`, `fabric_name`, `serial_number`, `role`, `mgmt_ip` |
| `vrfs` | `name`, `fabric_name`, `vrf_id`, `vlan_id` |
| `networks` | `name`, `fabric_name`, `vrf_name`, `network_id`, `vlan_id`, `gateway_ip` |
| `interfaces` | `name`, `switch_name`, `interface_type`, `mode` |

#### Response `200`

```json
{
  "status": "success",
  "imported": {
    "fabrics": 2,
    "switches": 12,
    "vrfs": 4,
    "networks": 20,
    "interfaces": 96
  },
  "errors": []
}
```

#### Response with partial errors `200`

```json
{
  "status": "partial",
  "imported": {
    "fabrics": 2,
    "switches": 10,
    "vrfs": 4,
    "networks": 18
  },
  "errors": [
    {"sheet": "switches", "row": 5, "error": "Duplicate serial number 'SAL123'"},
    {"sheet": "networks", "row": 12, "error": "VLAN 100 already used in fabric DC1"}
  ]
}
```

---

### `POST /api/v1/import/csv`

Bulk import from a CSV file.

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -F "file=@/path/to/switches.csv" \
  -F "resource_type=switches" \
  "http://<host>:8000/api/v1/import/csv"
```

#### Form Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | ✅ | CSV file |
| `resource_type` | string | ✅ | Enum: `fabrics`, `switches`, `vrfs`, `networks`, `interfaces` |

---

## 🚀 YAML Deploy

Generate YAML configuration and deploy via Ansible.

**Base path:** `/api/v1/deploy`

---

### `POST /api/v1/deploy/yaml`

Generate YAML configuration for a fabric.

#### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ✅ | Fabric to generate YAML for |
| `include` | list[string] | ❌ | Sections: `fabrics`, `vrfs`, `networks`, `switches`, `interfaces`, `vpc_peers`, `underlay`, `policies` |
| `format` | string | ❌ | Enum: `ansible`, `raw` (default: `ansible`) |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fabric_id": 1,
    "include": ["vrfs", "networks"],
    "format": "ansible"
  }' \
  "http://<host>:8000/api/v1/deploy/yaml"
```

#### Response `200`

```json
{
  "status": "success",
  "yaml_content": "---\nvxlan_fabric:\n  name: DC1_Fabric\n  vrfs:\n    - name: VRF_Production\n      vrf_id: 50001\n      ...",
  "download_url": "/api/v1/deploy/yaml/download/abc123"
}
```

---

### `GET /api/v1/deploy/yaml/download/{file_id}`

Download a previously generated YAML file.

```bash
curl -H "X-API-Key: your-key" \
  -o fabric_config.yml \
  "http://<host>:8000/api/v1/deploy/yaml/download/abc123"
```

---

### `POST /api/v1/deploy/run`

Trigger Ansible deployment using generated YAML.

#### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `fabric_id` | integer | ✅ | Fabric to deploy |
| `dry_run` | boolean | ❌ | Preview changes only (default: `false`) |
| `deploy_type` | string | ❌ | Enum: `full`, `vrfs`, `networks`, `interfaces` |

#### Request

```bash
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fabric_id": 1,
    "dry_run": true,
    "deploy_type": "full"
  }' \
  "http://<host>:8000/api/v1/deploy/run"
```

#### Response `200` (Dry Run)

```json
{
  "status": "dry_run",
  "task_id": "abc-123-def",
  "changes": {
    "vrfs_to_create": ["VRF_DMZ"],
    "vrfs_to_update": [],
    "networks_to_create": ["Net_App_Tier"],
    "networks_to_update": ["Net_Web_Tier"],
    "networks_to_delete": []
  }
}
```

#### Response `202` (Deployment Triggered)

```json
{
  "status": "accepted",
  "task_id": "abc-123-def",
  "message": "Deployment queued. Check status at /api/v1/deploy/status/abc-123-def"
}
```

---

### `GET /api/v1/deploy/status/{task_id}`

Check deployment status.

```bash
curl -H "X-API-Key: your-key" \
  "http://<host>:8000/api/v1/deploy/status/abc-123-def"
```

#### Response `200`

```json
{
  "task_id": "abc-123-def",
  "status": "completed",
  "started_at": "2026-03-30T10:00:00Z",
  "completed_at": "2026-03-30T10:02:30Z",
  "result": {
    "ok": 12,
    "changed": 5,
    "failed": 0,
    "skipped": 2
  }
}
```

---

## ❌ Error Reference

### Standard Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### All Error Codes

| Code | Type | When |
|---|---|---|
| `400` | `Bad Request` | Business logic violation (e.g., switch not in fabric) |
| `401` | `Unauthorized` | Missing or invalid `X-API-Key` header |
| `404` | `Not Found` | Resource with given ID doesn't exist |
| `409` | `Conflict` | Duplicate resource (name, VNI, VLAN, serial, etc.) |
| `422` | `Unprocessable Entity` | Request body validation failed (type, range, format) |
| `500` | `Internal Server Error` | Unexpected server error |

### Referential Integrity Errors (`400`)

| Error | Cause |
|---|---|
| `Fabric {id} does not exist` | Foreign key to non-existent fabric |
| `Switch {id} does not exist` | Foreign key to non-existent switch |
| `Switch {id} does not belong to fabric {id}` | Cross-fabric reference |
| `VRF {id} does not belong to fabric {id}` | Cross-fabric VRF reference |
| `VLAN {id} already used in fabric {id}` | Duplicate VLAN within fabric |
| `VNI {id} already used in fabric {id}` | Duplicate VNI within fabric |

---

## 🧪 Quick Start — End-to-End Example

### 1️⃣ Create a Fabric

```bash
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"name":"DC1","fabric_type":"VXLAN_EVPN","bgp_as":65001,"replication_mode":"multicast","anycast_gateway_mac":"2020.0000.00aa"}' \
  http://localhost:8000/api/v1/fabrics
```

### 2️⃣ Add Switches

```bash
# Spine
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"name":"DC1-Spine-01","fabric_id":1,"serial_number":"SAL001","role":"spine","mgmt_ip":"10.0.0.1","loopback0_ip":"10.2.0.1/32"}' \
  http://localhost:8000/api/v1/switches

# Leaf pair
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"name":"DC1-Leaf-01","fabric_id":1,"serial_number":"SAL011","role":"leaf","mgmt_ip":"10.0.0.11","loopback0_ip":"10.2.0.11/32","vtep_ip":"10.1.1.11"}' \
  http://localhost:8000/api/v1/switches

curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"name":"DC1-Leaf-02","fabric_id":1,"serial_number":"SAL012","role":"leaf","mgmt_ip":"10.0.0.12","loopback0_ip":"10.2.0.12/32","vtep_ip":"10.1.1.12"}' \
  http://localhost:8000/api/v1/switches
```

### 3️⃣ Set Up vPC Between Leaves

```bash
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"fabric_id":1,"switch1_id":2,"switch2_id":3,"vpc_domain_id":100,"peer_keepalive_src":"10.0.0.11","peer_keepalive_dst":"10.0.0.12","peer_link_port_channel":1,"peer_link_members":["Ethernet1/53","Ethernet1/54"]}' \
  http://localhost:8000/api/v1/vpc-peers
```

### 4️⃣ Configure Underlay

```bash
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"fabric_id":1,"routing_protocol":"ospf","ospf_area":"0.0.0.0","pim_rp_address":"10.254.254.1","bfd_enable":true}' \
  http://localhost:8000/api/v1/underlay
```

### 5️⃣ Create a VRF

```bash
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"name":"VRF_Prod","fabric_id":1,"vrf_id":50001,"vlan_id":2001,"attach_switches":[2,3]}' \
  http://localhost:8000/api/v1/vrfs
```

### 6️⃣ Create a Network

```bash
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"name":"Net_Web","fabric_id":1,"vrf_id":1,"network_id":30001,"vlan_id":100,"gateway_ip":"10.1.100.1/24","attach_switches":[{"switch_id":2,"ports":["Ethernet1/10"]},{"switch_id":3,"ports":["Ethernet1/10"]}]}' \
  http://localhost:8000/api/v1/networks
```

### 7️⃣ Generate YAML & Deploy

```bash
# Generate YAML
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"fabric_id":1,"format":"ansible"}' \
  http://localhost:8000/api/v1/deploy/yaml

# Dry run
curl -X POST -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"fabric_id":1,"dry_run":true}' \
  http://localhost:8000/api/v1/deploy/run
```

---

## 📊 Resource Relationship Diagram

```
Fabric (1)
├── Switches (many)
│   ├── Interfaces (many)
│   └── Policies (many)
├── VRFs (many)
│   └── Networks (many)
│       └── Switch Attachments (many)
├── vPC Peers (many)
├── Topology Links (many)
├── Underlay Config (one)
├── Overlay Extensions (many)
├── Route Control (many)
└── Global Config (many)
```

---

## 🔧 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NDFC_SOT_DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/ndfc_sot` | Database connection |
| `NDFC_SOT_API_KEYS` | `dev-api-key-change-in-production` | Comma-separated API keys |
| `NDFC_SOT_NDFC_URL` | — | NDFC controller URL |
| `NDFC_SOT_NDFC_USERNAME` | — | NDFC username |
| `NDFC_SOT_NDFC_PASSWORD` | — | NDFC password |
| `NDFC_SOT_NDFC_VERIFY_SSL` | `false` | Verify NDFC SSL cert |
| `NDFC_SOT_DEBUG` | `false` | Enable debug mode |
| `NDFC_SOT_LOG_LEVEL` | `INFO` | Log level |

---

> **Generated from source code on:** March 30, 2026  
> **For interactive Swagger UI:** Visit `http://<host>:8000/docs` (when accessible)  
> **For ReDoc:** Visit `http://<host>:8000/redoc` (when accessible)