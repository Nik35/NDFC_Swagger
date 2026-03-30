"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.exceptions import register_exception_handlers
from app.routers import (
    fabric,
    global_config,
    switches,
    interfaces,
    vpc_peers,
    topology,
    underlay,
    vrfs,
    networks,
    overlay_extensions,
    route_control,
    policy,
    yaml_deploy,
    import_router,
)

# ---------------------------------------------------------------------------
# Swagger tag metadata
# ---------------------------------------------------------------------------
tags_metadata = [
    {"name": "Fabrics", "description": "Manage NDFC fabric identity and type."},
    {"name": "Global", "description": "Fabric-wide global settings — BGP ASN, anycast GW MAC, DNS, NTP, syslog."},
    {"name": "Topology: Switches", "description": "Manage switch inventory — hostnames, serial numbers, roles, management IPs, POAP settings."},
    {"name": "Topology: Interfaces", "description": "Manage switch interfaces — access, trunk, port-channel, loopback, routed, sub-interface, breakout, dot1q-tunnel."},
    {"name": "Topology: vPC Peers", "description": "Manage virtual Port Channel peer pairs for leaf switch redundancy."},
    {"name": "Topology: Links", "description": "Manage fabric links, edge connections, and ToR peers."},
    {"name": "Underlay", "description": "Configure underlay fabric — general, IPv4, IPv6, IS-IS, OSPF, BGP, BFD, multicast. One config per fabric per section."},
    {"name": "Overlay: VRFs", "description": "Manage VRFs and their switch attachments."},
    {"name": "Overlay: Networks", "description": "Manage L2/L3 network segments, gateway IPs, DHCP relay, and switch attachments."},
    {"name": "Overlay Extensions", "description": "VRF Lite extensions and multisite configuration."},
    {"name": "Route Control", "description": "Manage prefix lists, community lists, AS-path access lists, route maps, IP ACLs, MAC lists, object groups, and time ranges."},
    {"name": "Policy", "description": "Manage freeform policies and policy groups."},
    {"name": "YAML & Deploy", "description": "Preview, download, and generate NAC-DC YAML for Ansible deployment."},
    {"name": "Import", "description": "Import full or partial NAC-DC YAML payloads via upsert."},
]


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Startup / shutdown lifecycle."""
    yield
    await engine.dispose()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RESTful Source of Truth for Cisco NDFC VXLAN EVPN fabrics. Generates NAC-DC YAML for Ansible deployment.",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Routers — all share the /api/v1 prefix
# ---------------------------------------------------------------------------
_prefix = settings.API_V1_PREFIX

app.include_router(fabric.router, prefix=_prefix)
app.include_router(global_config.router, prefix=_prefix)
app.include_router(switches.router, prefix=_prefix)
app.include_router(interfaces.router, prefix=_prefix)
app.include_router(vpc_peers.router, prefix=_prefix)
app.include_router(topology.router, prefix=_prefix)
app.include_router(underlay.router, prefix=_prefix)
app.include_router(vrfs.router, prefix=_prefix)
app.include_router(networks.router, prefix=_prefix)
app.include_router(overlay_extensions.router, prefix=_prefix)
app.include_router(route_control.router, prefix=_prefix)
app.include_router(policy.router, prefix=_prefix)
app.include_router(yaml_deploy.router, prefix=_prefix)
app.include_router(import_router.router, prefix=_prefix)


# ---------------------------------------------------------------------------
# Health check (no auth)
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe."""
    return {"status": "healthy", "version": settings.APP_VERSION}
