"""Import service — full and per-entity NAC-DC import via upsert.

Accepts a NAC-DC ``vxlan:`` dict and upserts all entities for the fabric.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.fabric_service import FabricService
from app.services.global_service import GlobalService
from app.services.overlay_extension_service import MultisiteService, VrfLiteExtensionService
from app.services.switch_service import SwitchService
from app.services.interface_service import InterfaceService
from app.services.vpc_peer_service import VpcPeerService
from app.services.topology_service import (
    FabricLinkService,
    EdgeConnectionService,
    TorPeerService,
)
from app.services.underlay_service import (
    UnderlayGeneralService,
    UnderlayIpv4Service,
    UnderlayIpv6Service,
    UnderlayIsisService,
    UnderlayOspfService,
    UnderlayBgpService,
    UnderlayBfdService,
    UnderlayMulticastService,
)
from app.services.vrf_service import VrfService
from app.services.network_service import NetworkService
from app.services.route_control_service import (
    Ipv4PrefixListService,
    Ipv6PrefixListService,
    StandardCommunityListService,
    ExtendedCommunityListService,
    IpAsPathAccessListService,
    RouteMapService,
    IpAclService,
    MacListService,
    ObjectGroupService,
    TimeRangeService,
)
from app.services.policy_service import PolicyService, PolicyGroupService


class ImportService:
    """Orchestrates full or partial NAC-DC import."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def import_full(self, payload: dict) -> dict:
        """Import an entire NAC-DC ``vxlan`` structure. Returns counts."""
        vxlan = payload.get("vxlan", payload)
        counts: dict[str, int] = {}

        # 1. Fabric
        fabric_data = vxlan.get("fabric")
        if not fabric_data:
            raise ValueError("Missing 'fabric' section")

        fabric_svc = FabricService(self.db)
        from app.models.fabric import FabricCreate

        fabric = await fabric_svc.upsert(
            FabricCreate(**fabric_data)
        )
        fabric_id = fabric.id
        counts["fabric"] = 1

        # 2. Global
        if "global" in vxlan:
            await GlobalService(self.db).upsert(fabric_id, vxlan["global"])
            counts["global"] = 1

        # 3. Multisite
        if "multisite" in vxlan:
            await MultisiteService(self.db).upsert(fabric_id, vxlan["multisite"])
            counts["multisite"] = 1

        # 4. Topology
        topo = vxlan.get("topology", {})

        if "switches" in topo:
            counts["switches"] = await self._import_switches(
                fabric_id, topo["switches"]
            )

        if "interfaces" in topo:
            counts["interfaces"] = await self._import_interfaces(
                fabric_id, topo["interfaces"]
            )

        if "vpc_peers" in topo:
            svc = VpcPeerService(self.db)
            for item in topo["vpc_peers"]:
                item["fabric_id"] = fabric_id
                await svc.upsert(item)
            counts["vpc_peers"] = len(topo["vpc_peers"])

        if "fabric_links" in topo:
            svc = FabricLinkService(self.db)
            for item in topo["fabric_links"]:
                item["fabric_id"] = fabric_id
                await svc.upsert(item)
            counts["fabric_links"] = len(topo["fabric_links"])

        if "edge_connections" in topo:
            svc = EdgeConnectionService(self.db)
            for item in topo["edge_connections"]:
                item["fabric_id"] = fabric_id
                await svc.upsert(item)
            counts["edge_connections"] = len(topo["edge_connections"])

        if "tor_peers" in topo:
            svc = TorPeerService(self.db)
            for item in topo["tor_peers"]:
                item["fabric_id"] = fabric_id
                await svc.upsert(item)
            counts["tor_peers"] = len(topo["tor_peers"])

        # 5. Underlay
        underlay = vxlan.get("underlay", {})
        underlay_map = {
            "general": UnderlayGeneralService,
            "ipv4": UnderlayIpv4Service,
            "ipv6": UnderlayIpv6Service,
            "isis": UnderlayIsisService,
            "ospf": UnderlayOspfService,
            "bgp": UnderlayBgpService,
            "bfd": UnderlayBfdService,
            "multicast": UnderlayMulticastService,
        }
        for key, svc_cls in underlay_map.items():
            if key in underlay:
                await svc_cls(self.db).upsert(fabric_id, underlay[key])
                counts[f"underlay_{key}"] = 1

        # 6. Overlay
        overlay = vxlan.get("overlay", {})

        if "vrfs" in overlay:
            vrf_svc = VrfService(self.db)
            for item in overlay["vrfs"]:
                item["fabric_id"] = fabric_id
                await vrf_svc.upsert(item)
            counts["vrfs"] = len(overlay["vrfs"])

        if "networks" in overlay:
            net_svc = NetworkService(self.db)
            for item in overlay["networks"]:
                item["fabric_id"] = fabric_id
                await net_svc.upsert(item)
            counts["networks"] = len(overlay["networks"])

        # 7. Overlay extensions
        extensions = vxlan.get("overlay_extensions", {})

        if "vrf_lite" in extensions:
            svc = VrfLiteExtensionService(self.db)
            for item in extensions["vrf_lite"]:
                item["fabric_id"] = fabric_id
                await svc.upsert(item)
            counts["vrf_lite"] = len(extensions["vrf_lite"])

        rc = extensions.get("route_control", {})
        rc_map = {
            "ipv4_prefix_lists": Ipv4PrefixListService,
            "ipv6_prefix_lists": Ipv6PrefixListService,
            "standard_community_lists": StandardCommunityListService,
            "extended_community_lists": ExtendedCommunityListService,
            "ip_as_path_access_lists": IpAsPathAccessListService,
            "route_maps": RouteMapService,
            "ip_acls": IpAclService,
            "mac_lists": MacListService,
            "object_groups": ObjectGroupService,
            "time_ranges": TimeRangeService,
        }
        for key, svc_cls in rc_map.items():
            if key in rc:
                svc = svc_cls(self.db)
                for item in rc[key]:
                    item["fabric_id"] = fabric_id
                    await svc.upsert(item)
                counts[key] = len(rc[key])

        # 8. Policy
        pol = vxlan.get("policy", {})

        if "policies" in pol:
            svc = PolicyService(self.db)
            for item in pol["policies"]:
                item["fabric_id"] = fabric_id
                await svc.upsert(item)
            counts["policies"] = len(pol["policies"])

        if "groups" in pol:
            svc = PolicyGroupService(self.db)
            for item in pol["groups"]:
                item["fabric_id"] = fabric_id
                await svc.upsert(item)
            counts["policy_groups"] = len(pol["groups"])

        await self.db.commit()
        return counts

    # ── per-entity import helpers ─────────────────────────────

    async def _import_switches(
        self, fabric_id: UUID, items: list[dict]
    ) -> int:
        from app.models.inventory import SwitchCreate

        svc = SwitchService(self.db)
        for item in items:
            item["fabric_id"] = fabric_id
            await svc.upsert(SwitchCreate(**item))
        return len(items)

    async def _import_interfaces(
        self, fabric_id: UUID, items: list[dict]
    ) -> int:
        """Import interfaces — resolve switch_name to switch_id."""
        switch_svc = SwitchService(self.db)
        iface_svc = InterfaceService(self.db)
        count = 0
        for item in items:
            switch_name = item.pop("switch_name", None)
            if not switch_name:
                continue
            sw = await switch_svc.get_by_name(fabric_id, switch_name)
            if not sw:
                continue
            item["switch_id"] = sw.id
            # Separate type_config from base fields
            base_fields = {
                "switch_id", "name", "type", "description",
                "admin_state", "mtu", "speed", "freeform_config",
            }
            type_config = {}
            base = {}
            for k, v in item.items():
                if k in base_fields:
                    base[k] = v
                elif k != "type_config":
                    type_config[k] = v
                else:
                    type_config.update(v)
            if type_config:
                base["type_config"] = type_config
            await iface_svc.upsert(base)
            count += 1
        return count

    async def import_switches(
        self, fabric_name: str, items: list[dict]
    ) -> int:
        fabric_svc = FabricService(self.db)
        fabric = await fabric_svc.get_by_name(fabric_name)
        if not fabric:
            raise ValueError(f"Fabric '{fabric_name}' not found")
        count = await self._import_switches(fabric.id, items)
        await self.db.commit()
        return count

    async def import_vrfs(
        self, fabric_name: str, items: list[dict]
    ) -> int:
        fabric_svc = FabricService(self.db)
        fabric = await fabric_svc.get_by_name(fabric_name)
        if not fabric:
            raise ValueError(f"Fabric '{fabric_name}' not found")
        vrf_svc = VrfService(self.db)
        for item in items:
            item["fabric_id"] = fabric.id
            await vrf_svc.upsert(item)
        await self.db.commit()
        return len(items)

    async def import_networks(
        self, fabric_name: str, items: list[dict]
    ) -> int:
        fabric_svc = FabricService(self.db)
        fabric = await fabric_svc.get_by_name(fabric_name)
        if not fabric:
            raise ValueError(f"Fabric '{fabric_name}' not found")
        net_svc = NetworkService(self.db)
        for item in items:
            item["fabric_id"] = fabric.id
            await net_svc.upsert(item)
        await self.db.commit()
        return len(items)
