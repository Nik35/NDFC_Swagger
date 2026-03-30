# NDFC Source-of-Truth (SoT) — Project Guide

> **Audience**: Developers, Tech Leads, and anyone new to NDFC / Data-Center Networking  
> **Last Updated**: March 25, 2026

---

## Table of Contents

1. [What is NDFC?](#1-what-is-ndfc)
2. [Why do we need a Source-of-Truth?](#2-why-do-we-need-a-source-of-truth)
3. [Architecture Overview](#3-architecture-overview)
4. [Data Flow Diagram](#4-data-flow-diagram)
5. [Entity Relationship Diagram](#5-entity-relationship-diagram)
6. [Layer-by-Layer Walkthrough](#6-layer-by-layer-walkthrough)
7. [Key Networking Concepts (Cheat Sheet)](#7-key-networking-concepts-cheat-sheet)
8. [API Endpoint Map](#8-api-endpoint-map)
9. [Deployment Flow](#9-deployment-flow)
10. [Questions to Ask Your Network Engineering Team](#10-questions-to-ask-your-network-engineering-team)
11. [Glossary](#11-glossary)

---

## 1. What is NDFC?

### Full Form

**NDFC = Nexus Dashboard Fabric Controller**  
(Previously known as **DCNM** — Data Center Network Manager)

### What does it do?

NDFC is **Cisco's controller software** that manages the entire lifecycle of
data-center network fabrics. Think of it as the "brain" that:

```
┌─────────────────────────────────────────────────────┐
│                    NDFC Controller                    │
│                                                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │ Discover │  │ Provision│  │ Monitor │  │ Deploy │ │
│  │ Switches │  │ Configs  │  │ Health  │  │ Configs│ │
│  └─────────┘  └─────────┘  └─────────┘  └────────┘ │
│                                                       │
│  Manages: VXLAN EVPN Fabrics, VRFs, Networks,        │
│           Interfaces, Policies, vPC Peers             │
└──────────────────────┬──────────────────────────────┘
                       │ SSH / REST API / gRPC
          ┌────────────┼────────────────┐
          │            │                │
     ┌────▼───┐  ┌────▼───┐  ┌────────▼──┐
     │ Spine  │  │ Spine  │  │  Border   │
     │ Switch │  │ Switch │  │  Gateway  │
     └────┬───┘  └────┬───┘  └────────┬──┘
          │            │               │
     ┌────▼───┐  ┌────▼───┐  ┌────────▼──┐
     │  Leaf  │  │  Leaf  │  │   Leaf    │
     │ Switch │  │ Switch │  │  Switch   │
     └────────┘  └────────┘  └───────────┘
```

### Key Capabilities

| Capability | Description |
|-----------|-------------|
| **Fabric Management** | Create and manage VXLAN EVPN fabrics |
| **Switch Discovery** | Auto-discover and onboard Nexus switches |
| **Configuration** | Push VRFs, Networks, Interfaces, Policies |
| **Monitoring** | Real-time health, alarms, topology view |
| **Compliance** | Detect config drift, enforce intent |
| **Multi-Site** | Connect multiple fabrics via Multi-Site Domain (MSD) |

### NDFC REST API

NDFC exposes a **REST API** (typically at `https://<ndfc-ip>/appcenter/cisco/ndfc/api/v1/...`).
Our application uses this API to **push configurations** generated from our SoT database.

---

## 2. Why do we need a Source-of-Truth?

### The Problem

```
WITHOUT SoT:
                                                          
  Engineer A ──► NDFC GUI ──► Push Config (Fabric-1)     
  Engineer B ──► NDFC GUI ──► Push Config (Fabric-1)     ← CONFLICT!
  Engineer C ──► CLI/SSH  ──► Direct Switch Config       ← CONFIG DRIFT!
                                                          
  Result: Nobody knows the "correct" intended state.      
```

### The Solution

```
WITH SoT:
                                                          
  Engineer A ─┐                                           
  Engineer B ─┼──► SoT API ──► PostgreSQL ──► YAML ──► Ansible ──► NDFC
  Engineer C ─┘    (Single                    (Git-     (Automation)
                    Source)                    tracked)  
                                                          
  Result: One truth. Versioned. Auditable. Automated.    
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Single Source of Truth** | All intended network state lives in one database |
| **Version Control** | Every change is tracked; rollback is possible |
| **Validation** | API validates data BEFORE it reaches the network |
| **Automation** | YAML → Ansible → NDFC pipeline removes manual errors |
| **Auditability** | Who changed what and when |
| **CI/CD** | Network changes follow the same pipeline as application code |

---

## 3. Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                        NDFC SoT Application                        │
│                                                                    │
│  ┌──────────┐   ┌───────────┐   ┌───────────┐   ┌─────────────┐  │
│  │  FastAPI  │   │  Pydantic │   │SQLAlchemy │   │  PostgreSQL │  │
│  │  Routers  │──▶│  Models   │──▶│  Services │──▶│  Database   │  │
│  │ (10 files)│   │(Validate) │   │ (11 files)│   │  (Tables)   │  │
│  └──────────┘   └───────────┘   └───────────┘   └─────────────┘  │
│       │                                                │           │
│       │              ┌─────────────┐                   │           │
│       └─────────────▶│ YAML Builder│◀──────────────────┘           │
│                      │  Service    │                               │
│                      └──────┬──────┘                               │
│                             │                                      │
│                      ┌──────▼──────┐                               │
│                      │   Celery    │                               │
│                      │   Workers   │                               │
│                      └──────┬──────┘                               │
│                             │                                      │
│                      ┌──────▼──────┐                               │
│                      │  Ansible    │                               │
│                      │  Deployer   │                               │
│                      └──────┬──────┘                               │
└─────────────────────────────┼──────────────────────────────────────┘
                              │
                       ┌──────▼──────┐
                       │    NDFC     │
                       │ Controller  │
                       └──────┬──────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
            ┌────▼──┐   ┌────▼──┐   ┌────▼──┐
            │Spine 1│   │Spine 2│   │Border │
            └───┬───┘   └───┬───┘   └───┬───┘
                │           │           │
            ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
            │Leaf 1 │   │Leaf 2 │   │Leaf 3 │
            └───────┘   └───────┘   └───────┘
```

---

## 4. Data Flow Diagram

### End-to-End Flow

```
 ┌──────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
 │ User │────▶│ FastAPI  │────▶│ Pydantic │────▶│ Service  │
 │(API) │     │ Router   │     │Validation│     │  Layer   │
 └──────┘     └──────────┘     └──────────┘     └─────┬────┘
                                                       │
                                                       ▼
 ┌──────────┐     ┌──────────┐     ┌──────────┐  ┌──────────┐
 │  NDFC    │◀────│ Ansible  │◀────│  Celery  │◀─│PostgreSQL│
 │Controller│     │ Deployer │     │  Worker  │  │ Database │
 └──────────┘     └──────────┘     └──────────┘  └──────────┘
```

### Step-by-Step

```
Step 1: CREATE  ─── User sends POST /api/v1/fabrics
                    ├── Pydantic validates payload
                    ├── Service creates DB record
                    └── Returns FabricRead response

Step 2: BUILD   ─── User adds switches, VRFs, networks, policies
                    ├── Each entity validated (referential integrity)
                    └── All stored in PostgreSQL

Step 3: PREVIEW ─── User calls GET /api/v1/yaml/{fabric_id}
                    ├── YAML Builder reads ALL entities for fabric
                    ├── Constructs Ansible-compatible YAML structure
                    └── Returns preview JSON

Step 4: DEPLOY  ─── User calls POST /api/v1/deploy/{fabric_id}
                    ├── Celery task created (returns task_id)
                    ├── Worker generates YAML files to disk
                    ├── Worker invokes Ansible playbook
                    ├── Ansible pushes config to NDFC via REST API
                    └── NDFC deploys to physical switches

Step 5: STATUS  ─── User polls GET /api/v1/status/{task_id}
                    ├── Returns PENDING / STARTED / SUCCESS / FAILURE
                    └── On SUCCESS, includes deployment result
```

---

## 5. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ENTITY RELATIONSHIPS                             │
│                                                                          │
│  ┌──────────┐ 1    * ┌──────────┐ 1    * ┌──────────────┐              │
│  │  FABRIC  │───────▶│  SWITCH  │───────▶│  INTERFACE   │              │
│  │          │        │          │        │              │              │
│  │ name     │        │ hostname │        │ name         │              │
│  │ type     │        │ role     │        │ type         │              │
│  │ bgp_as   │        │ mgmt_ip  │        │ mode         │              │
│  └────┬─────┘        └──────────┘        └──────────────┘              │
│       │                                                                  │
│       │ 1    *  ┌──────────┐                                            │
│       ├────────▶│   VRF    │                                            │
│       │         │          │                                            │
│       │         │ name     │                                            │
│       │         │ vni      │                                            │
│       │         │ rt / rd  │                                            │
│       │         └────┬─────┘                                            │
│       │              │ 1    *                                            │
│       │         ┌────▼─────┐                                            │
│       │         │ NETWORK  │                                            │
│       │         │          │                                            │
│       │         │ name     │                                            │
│       │         │ vlan_id  │                                            │
│       │         │ vni      │                                            │
│       │         │ gateway  │                                            │
│       │         └──────────┘                                            │
│       │                                                                  │
│       │ 1    1  ┌──────────┐                                            │
│       ├────────▶│ UNDERLAY │                                            │
│       │         │          │                                            │
│       │         │ protocol │                                            │
│       │         │ multicast│                                            │
│       │         └──────────┘                                            │
│       │                                                                  │
│       │ 1    *  ┌──────────┐                                            │
│       ├────────▶│ VPC_PEER │                                            │
│       │         │          │                                            │
│       │         │ peer1    │                                            │
│       │         │ peer2    │                                            │
│       │         │ domain_id│                                            │
│       │         └──────────┘                                            │
│       │                                                                  │
│       │ 1    *  ┌──────────┐     ┌──────────────┐     ┌─────────────┐  │
│       ├────────▶│  POLICY  │     │ POLICY_GROUP │────▶│ ASSIGNMENT  │  │
│       │         │ GROUP    │◀────│              │     │             │  │
│       │         └──────────┘     └──────────────┘     └─────────────┘  │
│       │                                                                  │
│       │ 1    *  ┌───────────────────────────────────────┐               │
│       └────────▶│        ROUTE CONTROL                   │               │
│                 │                                         │               │
│                 │  ┌──────────────┐  ┌─────────────────┐ │               │
│                 │  │IPv4 Prefix   │  │IPv6 Prefix      │ │               │
│                 │  │List          │  │List             │ │               │
│                 │  └──────────────┘  └─────────────────┘ │               │
│                 │  ┌──────────────┐  ┌─────────────────┐ │               │
│                 │  │Std Community │  │Ext Community    │ │               │
│                 │  │List          │  │List             │ │               │
│                 │  └──────────────┘  └─────────────────┘ │               │
│                 │  ┌──────────────┐  ┌─────────────────┐ │               │
│                 │  │AS-Path Access│  │Route Map        │ │               │
│                 │  │List          │  │                 │ │               │
│                 │  └──────────────┘  └─────────────────┘ │               │
│                 │  ┌──────────────┐                       │               │
│                 │  │Time Range    │                       │               │
│                 │  └──────────────┘                       │               │
│                 └───────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Layer-by-Layer Walkthrough

### 6.1 Routers Layer (`app/routers/`)

The entry point for all HTTP requests.

| Router File | Prefix | Responsibility |
|------------|--------|----------------|
| `fabric.py` | `/api/v1/fabrics` | CRUD for fabrics |
| `switches.py` | `/api/v1/switches` | CRUD for switches |
| `interfaces.py` | `/api/v1/interfaces` | CRUD for interfaces |
| `vrfs.py` | `/api/v1/vrfs` | CRUD for VRFs |
| `networks.py` | `/api/v1/networks` | CRUD for networks |
| `underlay.py` | `/api/v1/underlay` | CRUD for underlay + multicast |
| `vpc_peers.py` | `/api/v1/vpc-peers` | CRUD for vPC peer pairs |
| `policy.py` | `/api/v1/policies` | CRUD for policies, groups, assignments |
| `route_control.py` | `/api/v1/route-control` | CRUD for prefix lists, community lists, route maps, etc. |
| `yaml_deploy.py` | `/api/v1` | YAML preview, generation, deployment, task status |

### 6.2 Models Layer (`app/models/`)

**Pydantic models** for request/response validation.

```
app/models/
├── common.py              # BaseRead with id + timestamps
├── fabric.py              # FabricCreate, FabricRead, FabricUpdate
├── inventory.py           # SwitchCreate, SwitchRead, SwitchUpdate
├── topology.py            # Link / topology models
├── deploy.py              # Deploy request / response
├── yaml_models.py         # Full YAML document structure
├── overlay/
│   ├── vrf.py             # VrfCreate, VrfRead, VrfUpdate
│   └── network.py         # NetworkCreate, NetworkRead, NetworkUpdate
├── underlay/
│   ├── general.py         # General underlay settings
│   └── multicast.py       # Multicast / PIM config
├── interfaces/
│   ├── routed.py          # Routed interface model
│   ├── trunk.py           # Trunk / access interface model
│   └── port_channel.py    # Port-channel / vPC model
├── policy/
│   ├── policy.py          # Policy model
│   └── policy_group.py    # Policy group + assignment
└── route_control/
    ├── prefix_list.py     # IPv4/IPv6 prefix lists
    ├── community_list.py  # Standard/extended community lists
    ├── as_path.py         # AS-path access lists
    ├── route_map.py       # Route maps with entries
    └── time_range.py      # Time-based access rules
```

### 6.3 DB Models Layer (`app/db_models/`)

**SQLAlchemy ORM models** mapped to PostgreSQL tables.

```
app/db_models/
├── base.py                # Declarative base + UUID mixin
├── fabric.py              # fabrics table
├── switch.py              # switches table
├── interface.py           # interfaces table
├── vrf.py                 # vrfs table
├── network.py             # networks table
├── underlay.py            # underlay_configs + multicast_configs tables
├── vpc_peer.py            # vpc_peers table
├── policy.py              # policies + policy_groups + policy_assignments
├── route_control.py       # 7 route-control tables
└── __init__.py            # Re-exports all models for Alembic
```

### 6.4 Services Layer (`app/services/`)

**Business logic** — sits between routers and database.

```
app/services/
├── fabric_service.py      # Fabric CRUD operations
├── switch_service.py      # Switch CRUD + bulk create
├── interface_service.py   # Interface CRUD + bulk create
├── vrf_service.py         # VRF CRUD
├── network_service.py     # Network CRUD
├── underlay_service.py    # Underlay + Multicast CRUD
├── vpc_peer_service.py    # vPC Peer CRUD
├── policy_service.py      # Policy + Group + Assignment CRUD
├── route_control_service.py # All route-control entity CRUD
├── yaml_builder.py        # Reads DB → builds YAML structure
└── ansible_deployer.py    # Writes YAML files → runs Ansible
```

### 6.5 Tasks Layer (`app/tasks/`)

**Celery async tasks** for long-running operations.

```
app/tasks/
├── celery_app.py          # Celery application + Redis broker config
└── deploy_tasks.py        # generate_yaml_task, deploy_fabric_task
```

### 6.6 Validators (`app/validators/`)

```
app/validators/
└── referential.py         # Cross-entity validation
                           # e.g., "Does this fabric_id exist?"
                           # e.g., "Does this VRF exist in the fabric?"
```

---

## 7. Key Networking Concepts (Cheat Sheet)

| Concept | What It Means | Analogy |
|---------|--------------|---------|
| **Fabric** | A group of interconnected switches forming a network domain | A "project" or "environment" |
| **Spine** | Top-of-rack aggregation switch (routes traffic between leaves) | Highway interchange |
| **Leaf** | Access switch (servers/hosts connect here) | Local road |
| **Border Gateway** | Connects the fabric to external networks | City border checkpoint |
| **VXLAN** | Virtual Extensible LAN — tunneling protocol to stretch L2 over L3 | VPN tunnel for local networks |
| **EVPN** | Ethernet VPN — BGP-based control plane for VXLAN | GPS routing for VXLAN tunnels |
| **VRF** | Virtual Routing & Forwarding — isolated routing table | Separate apartment in a building |
| **VNI** | VXLAN Network Identifier — unique ID for each segment | ZIP code for a network |
| **BGP AS** | Border Gateway Protocol Autonomous System number | Country code for a network domain |
| **vPC** | Virtual Port Channel — two switches acting as one | Dual power supply (redundancy) |
| **Underlay** | Physical network (OSPF/ISIS + PIM) that carries VXLAN traffic | Road infrastructure |
| **Overlay** | Virtual networks (VRFs + Networks) on top of underlay | Cars driving on the roads |
| **PIM** | Protocol Independent Multicast — for BUM traffic | Broadcasting to multiple TVs |
| **Route Map** | Filter/modify routes as they enter or leave | Customs inspection rules |
| **Prefix List** | List of IP subnets used in route filtering | Approved address list |
| **Community List** | Tags attached to BGP routes for policy decisions | Luggage tags at an airport |

---

## 8. API Endpoint Map

### Fabric Lifecycle

```
POST   /api/v1/fabrics                          Create fabric
GET    /api/v1/fabrics                          List fabrics
GET    /api/v1/fabrics/{id}                     Get fabric
PATCH  /api/v1/fabrics/{id}                     Update fabric
DELETE /api/v1/fabrics/{id}                     Delete fabric
```

### Switches

```
POST   /api/v1/switches                         Create switch
POST   /api/v1/switches/bulk                    Create multiple
GET    /api/v1/switches/fabric/{fabric_id}      List by fabric
GET    /api/v1/switches/{id}                    Get switch
PATCH  /api/v1/switches/{id}                    Update switch
DELETE /api/v1/switches/{id}                    Delete switch
```

### Interfaces

```
POST   /api/v1/interfaces/switch/{switch_id}         Create interface
POST   /api/v1/interfaces/switch/{switch_id}/bulk    Bulk create
GET    /api/v1/interfaces/switch/{switch_id}         List by switch
GET    /api/v1/interfaces/{id}                       Get interface
PATCH  /api/v1/interfaces/{id}                       Update
DELETE /api/v1/interfaces/{id}                       Delete
```

### VRFs & Networks

```
POST   /api/v1/vrfs                             Create VRF
GET    /api/v1/vrfs/fabric/{fabric_id}          List by fabric
GET    /api/v1/vrfs/{id}                        Get VRF
PATCH  /api/v1/vrfs/{id}                        Update VRF
DELETE /api/v1/vrfs/{id}                        Delete VRF

POST   /api/v1/networks                         Create Network
GET    /api/v1/networks/fabric/{fabric_id}      List by fabric
GET    /api/v1/networks/{id}                    Get Network
PATCH  /api/v1/networks/{id}                    Update Network
DELETE /api/v1/networks/{id}                    Delete Network
```

### Underlay & vPC

```
POST   /api/v1/underlay/fabric/{fabric_id}              Create underlay
GET    /api/v1/underlay/fabric/{fabric_id}              Get underlay
PUT    /api/v1/underlay/fabric/{fabric_id}/multicast    Upsert multicast
DELETE /api/v1/underlay/fabric/{fabric_id}/multicast    Delete multicast

POST   /api/v1/vpc-peers/fabric/{fabric_id}     Create vPC pair
GET    /api/v1/vpc-peers/fabric/{fabric_id}     List by fabric
PATCH  /api/v1/vpc-peers/{id}                   Update
DELETE /api/v1/vpc-peers/{id}                   Delete
```

### Policies & Route Control

```
POST   /api/v1/policies/fabric/{fabric_id}      Create policy
GET    /api/v1/policies/fabric/{fabric_id}      List policies
POST   /api/v1/policies/groups/fabric/{id}      Create group
POST   /api/v1/policies/groups/{id}/assignments Assign switch

POST   /api/v1/route-control/ipv4-prefix-lists/fabric/{id}   Create prefix list
POST   /api/v1/route-control/route-maps/fabric/{id}          Create route map
... (similar pattern for all route-control sub-resources)
```

### Deploy & Status

```
GET    /api/v1/yaml/{fabric_id}                 Preview YAML
POST   /api/v1/yaml/{fabric_id}                 Generate YAML (async)
POST   /api/v1/deploy/{fabric_id}               Deploy (async)
GET    /api/v1/status/{task_id}                 Check task status
```

---

## 9. Deployment Flow

### Sequence Diagram

```
 Developer          SoT API          PostgreSQL       Celery Worker      Ansible         NDFC
    │                  │                 │                 │                │              │
    │  POST /fabrics   │                 │                 │                │              │
    │─────────────────▶│  INSERT fabric  │                 │                │              │
    │                  │────────────────▶│                 │                │              │
    │  201 Created     │                 │                 │                │              │
    │◀─────────────────│                 │                 │                │              │
    │                  │                 │                 │                │              │
    │  POST /switches  │                 │                 │                │              │
    │─────────────────▶│  INSERT switch  │                 │                │              │
    │                  │────────────────▶│                 │                │              │
    │  ... (add VRFs, networks, etc.)   │                 │                │              │
    │                  │                 │                 │                │              │
    │  POST /deploy/x  │                 │                 │                │              │
    │─────────────────▶│  Queue task     │                 │                │              │
    │  202 {task_id}   │─────────────────────────────────▶│                │              │
    │◀─────────────────│                 │                 │                │              │
    │                  │                 │    Read all     │                │              │
    │                  │                 │◀────────────────│                │              │
    │                  │                 │    entities     │                │              │
    │                  │                 │────────────────▶│                │              │
    │                  │                 │                 │  Build YAML    │              │
    │                  │                 │                 │───────────────▶│              │
    │                  │                 │                 │                │  REST API    │
    │                  │                 │                 │                │─────────────▶│
    │                  │                 │                 │                │              │
    │                  │                 │                 │                │  Push configs│
    │                  │                 │                 │                │  to switches │
    │                  │                 │                 │                │              │
    │  GET /status/x   │                 │                 │                │              │
    │─────────────────▶│  Check result   │                 │                │              │
    │  {status:SUCCESS}│◀────────────────────────────────│                │              │
    │◀─────────────────│                 │                 │                │              │
```

### Deployment Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Preview** | `GET /yaml/{id}` — returns YAML as JSON | Review before committing |
| **Generate** | `POST /yaml/{id}` — writes files to disk | Pre-stage for manual Ansible run |
| **Deploy** | `POST /deploy/{id}` — full auto pipeline | Production push |
| **Check Mode** | `POST /deploy/{id}` with `check_mode: true` | Dry run / diff only |

---

## 10. Questions to Ask Your Network Engineering Team

### 🔵 Understanding Requirements

| # | Question | Why You Need This |
|---|----------|-------------------|
| 1 | **What NDFC version are we targeting?** (12.x? 12.1.3?) | API endpoints and payload schemas differ between versions |
| 2 | **How many fabrics will we manage?** (1? 5? 50?) | Impacts database sizing, indexing, and multi-tenancy design |
| 3 | **What fabric types do we need?** (VXLAN EVPN only? or also LAN Classic, External?) | Determines which NDFC templates/policies we need to support |
| 4 | **Are we managing MSD (Multi-Site Domain)?** | Adds an MSD fabric entity + inter-fabric links |

### 🟢 Overlay (VRFs & Networks)

| # | Question | Why You Need This |
|---|----------|-------------------|
| 5 | **What is the VNI allocation scheme?** (manual? auto-range?) | Our VNI fields need validation ranges |
| 6 | **Do VRFs use auto-generated or manual RT/RD values?** | Affects whether we compute or store these |
| 7 | **Do networks need DHCP relay? If yes, what are the DHCP server IPs?** | We may need `dhcp_server_addr` fields |
| 8 | **Are there L2-only networks** (no gateway, no VRF)? | Our `is_l2_only` flag needs to be handled in YAML |
| 9 | **Do networks attach to specific leaf switches or all leaves?** | Impacts our network-to-switch mapping |

### 🟡 Underlay

| # | Question | Why You Need This |
|---|----------|-------------------|
| 10 | **OSPF or IS-IS for underlay routing?** | Different config templates |
| 11 | **What is the OSPF area ID / IS-IS NET?** | Stored in underlay config |
| 12 | **Multicast (PIM + RP) or Ingress Replication?** | Completely different underlay config |
| 13 | **If PIM, is the RP static, BSR, or Phantom?** | Different RP config blocks |

### 🟠 Switches & Interfaces

| # | Question | Why You Need This |
|---|----------|-------------------|
| 14 | **What switch roles are in scope?** (Spine, Leaf, Border, Border-Spine, Border-Gateway, Super-Spine?) | Our `role` enum must match |
| 15 | **What NX-OS versions are on the switches?** | Some features need specific versions |
| 16 | **What interface types do we configure?** (routed, trunk, access, loopback, port-channel, vPC?) | Determines our interface models |
| 17 | **Do we manage physical breakout ports?** (e.g., 40G → 4x10G) | Additional config step |

### 🔴 vPC & Redundancy

| # | Question | Why You Need This |
|---|----------|-------------------|
| 18 | **How are vPC pairs defined?** (which leaf pairs?) | Our vpc_peer entity needs correct switch pairing |
| 19 | **What vPC domain IDs are used?** (auto or manual?) | Stored in our vpc_peers table |
| 20 | **Is vPC auto-peer-link used, or do we define the peer-link interfaces?** | Impacts interface config |

### 🟣 Policy & Route Control

| # | Question | Why You Need This |
|---|----------|-------------------|
| 21 | **What NDFC policy templates do we need?** (e.g., `leaf_freeform`, `switch_freeform`, `interface_freeform`?) | Maps to our `template_name` field |
| 22 | **Do we need route maps for inter-VRF leaking?** | Additional route_map entries |
| 23 | **Are there external BGP peers?** (for Border Gateways) | May need BGP neighbor config |
| 24 | **Do we need ACLs (Access Control Lists)?** | May need an additional entity |

### ⚫ Deployment & Operations

| # | Question | Why You Need This |
|---|----------|-------------------|
| 25 | **What is the Ansible version and collection?** (`cisco.dcnm`? `cisco.ndfc`?) | Determines playbook module names |
| 26 | **Does the team want check-mode (dry run) before every deploy?** | Workflow design |
| 27 | **How do we handle config drift?** (alert only? auto-remediate?) | Future feature scope |
| 28 | **Do we need rollback capability?** | Must store config snapshots |
| 29 | **What's the change approval workflow?** (auto-deploy? manual approve?) | May need approval status field |
| 30 | **What credentials does our app use to talk to NDFC?** (service account? token?) | Auth config |

### 🔶 Integration & Day-2

| # | Question | Why You Need This |
|---|----------|-------------------|
| 31 | **Should we integrate with NDFC's built-in image management?** | Separate feature module |
| 32 | **Do we need to sync state FROM NDFC back to SoT?** (reconciliation) | Reverse-sync service |
| 33 | **Are there existing ServiceNow / ITSM integrations needed?** | Webhook / event design |
| 34 | **Do we need multi-user role-based access?** (admin vs read-only) | Auth / RBAC layer |
| 35 | **What is the target SLA for deployments?** (minutes? hours?) | Queue sizing / scaling |

---

## 11. Glossary

| Term | Full Form | Description |
|------|-----------|-------------|
| **NDFC** | Nexus Dashboard Fabric Controller | Cisco's DC fabric management platform |
| **DCNM** | Data Center Network Manager | Predecessor name of NDFC |
| **SoT** | Source of Truth | Single authoritative data store for intended state |
| **VXLAN** | Virtual Extensible LAN | Overlay tunneling protocol (RFC 7348) |
| **EVPN** | Ethernet VPN | BGP address family for MAC/IP advertisement |
| **VRF** | Virtual Routing & Forwarding | Isolated routing instance |
| **VNI** | VXLAN Network Identifier | 24-bit ID (1–16,777,215) for each segment |
| **BGP** | Border Gateway Protocol | Routing protocol used for EVPN control plane |
| **AS** | Autonomous System | A network under single administrative control |
| **OSPF** | Open Shortest Path First | Interior gateway routing protocol |
| **IS-IS** | Intermediate System to IS | Alternative interior gateway protocol |
| **PIM** | Protocol Independent Multicast | Multicast routing protocol for BUM traffic |
| **RP** | Rendezvous Point | Meeting point for multicast sources/receivers |
| **vPC** | Virtual Port Channel | Cisco feature: two switches act as one |
| **RT** | Route Target | BGP extended community for VPN import/export |
| **RD** | Route Distinguisher | Makes VPN routes unique in BGP table |
| **BUM** | Broadcast, Unknown Unicast, Multicast | Traffic types that need special handling in VXLAN |
| **MSD** | Multi-Site Domain | NDFC fabric type connecting multiple VXLAN fabrics |
| **NX-OS** | Nexus Operating System | Cisco's OS for Nexus data-center switches |
| **Ansible** | — | IT automation tool (YAML playbooks) |
| **Celery** | — | Python distributed task queue |
| **Redis** | — | In-memory data store (used as Celery broker) |
| **Alembic** | — | SQLAlchemy database migration tool |
| **FastAPI** | — | High-performance Python web framework |
| **Pydantic** | — | Python data validation library |

---

## Quick Start

```bash
# 1. Clone & install
cd e:\Training-Nikhil\NW_POC\ndfc-sot
pip install -r requirements.txt

# 2. Set environment variables
set NDFC_SOT_DB_URL=postgresql+asyncpg://user:pass@localhost:5432/ndfc_sot
set NDFC_SOT_API_KEY=your-secret-key
set NDFC_SOT_REDIS_URL=redis://localhost:6379/0

# 3. Run database migrations
alembic upgrade head

# 4. Start the API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Start Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# 6. Open Swagger docs
# http://localhost:8000/docs
```

---

> **💡 Tip**: Share this document with your network engineering team and use  
> Section 10 as a structured interview guide. Their answers will directly  
> inform which fields, enums, and validation rules need to be adjusted in  
> our Pydantic models and database schema.