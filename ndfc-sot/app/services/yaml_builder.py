"""YAML builder – converts DB state into NAC-DC compatible YAML dicts.

Queries ALL entities for a fabric and builds the exact structure expected
by the ``cisco.dcnm`` Ansible collection.  Empty sections are omitted.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.fabric import FabricDB
from app.db_models.global_config import FabricGlobalDB
from app.db_models.multisite import MultisiteDB
from app.db_models.switch import SwitchDB
from app.db_models.interface import InterfaceDB
from app.db_models.vpc_peer import VpcPeerDB
from app.db_models.topology import FabricLinkDB, EdgeConnectionDB, TorPeerDB
from app.db_models.underlay import (
    UnderlayGeneralDB,
    UnderlayIpv4DB,
    UnderlayIpv6DB,
    UnderlayIsisDB,
    UnderlayOspfDB,
    UnderlayBgpDB,
    UnderlayBfdDB,
    UnderlayMulticastDB,
)
from app.db_models.vrf import VrfDB, VrfSwitchAttachmentDB
from app.db_models.network import NetworkDB, NetworkSwitchAttachmentDB
from app.db_models.overlay_extensions import VrfLiteExtensionDB
from app.db_models.route_control import (
    Ipv4PrefixListDB,
    Ipv6PrefixListDB,
    StandardCommunityListDB,
    ExtendedCommunityListDB,
    IpAsPathAccessListDB,
    RouteMapDB,
    IpAclDB,
    MacListDB,
    ObjectGroupDB,
    TimeRangeDB,
)
from app.db_models.policy import PolicyDB, PolicyGroupDB

# Columns to always strip from YAML output
_SKIP = frozenset({"id", "fabric_id", "created_at", "updated_at"})


def _row_to_dict(row, *, skip: frozenset[str] = _SKIP) -> dict:
    """Convert a SQLAlchemy model instance to a dict, omitting None values and internal columns."""
    result: dict = {}
    for col in row.__table__.columns:
        if col.name in skip:
            continue
        val = getattr(row, col.name)
        if val is not None:
            result[col.name] = val
    return result


class YamlBuilder:
    """Builds a complete NAC-DC YAML dict for a fabric."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def build_fabric_yaml(self, fabric_id: UUID) -> dict:
        """Build the complete ``vxlan:`` YAML structure for a fabric."""
        vxlan: dict = {}

        # ── fabric ────────────────────────────────────────────
        fabric = await self._one(FabricDB, fabric_id, pk="id")
        if not fabric:
            raise ValueError(f"Fabric {fabric_id} not found")
        vxlan["fabric"] = {"name": fabric.name, "type": fabric.type}

        # ── global ────────────────────────────────────────────
        glob = await self._one(FabricGlobalDB, fabric_id)
        if glob:
            vxlan["global"] = _row_to_dict(glob)

        # ── multisite ─────────────────────────────────────────
        ms = await self._one(MultisiteDB, fabric_id)
        if ms:
            vxlan["multisite"] = _row_to_dict(ms)

        # ── topology ──────────────────────────────────────────
        topology: dict = {}

        switches = await self._many(SwitchDB, fabric_id)
        if switches:
            switch_list = [_row_to_dict(s) for s in switches]
            # Fetch interfaces and nest under switches
            interfaces = await self._interfaces_for_fabric(fabric_id)
            if interfaces:
                for sw in switch_list:
                    sw_name = sw.get("name")
                    if sw_name in interfaces:
                        sw["interfaces"] = interfaces[sw_name]
            topology["switches"] = switch_list

        vpc_peers = await self._many(VpcPeerDB, fabric_id)
        if vpc_peers:
            topology["vpc_peers"] = [_row_to_dict(v) for v in vpc_peers]

        fabric_links = await self._many(FabricLinkDB, fabric_id)
        if fabric_links:
            topology["fabric_links"] = [_row_to_dict(fl) for fl in fabric_links]

        edge_conns = await self._many(EdgeConnectionDB, fabric_id)
        if edge_conns:
            topology["edge_connections"] = [_row_to_dict(ec) for ec in edge_conns]

        tor_peers = await self._many(TorPeerDB, fabric_id)
        if tor_peers:
            topology["tor_peers"] = [_row_to_dict(tp) for tp in tor_peers]

        if topology:
            vxlan["topology"] = topology

        # ── underlay ──────────────────────────────────────────
        underlay: dict = {}
        for key, model in [
            ("general", UnderlayGeneralDB),
            ("ipv4", UnderlayIpv4DB),
            ("ipv6", UnderlayIpv6DB),
            ("isis", UnderlayIsisDB),
            ("ospf", UnderlayOspfDB),
            ("bgp", UnderlayBgpDB),
            ("bfd", UnderlayBfdDB),
            ("multicast", UnderlayMulticastDB),
        ]:
            row = await self._one(model, fabric_id)
            if row:
                underlay[key] = _row_to_dict(row)
        if underlay:
            vxlan["underlay"] = underlay

        # ── overlay ───────────────────────────────────────────
        overlay: dict = {}

        vrfs = await self._many(VrfDB, fabric_id)
        if vrfs:
            vrf_list, vrf_attach_groups = await self._build_vrfs(vrfs)
            overlay["vrfs"] = vrf_list
            if vrf_attach_groups:
                overlay["vrf_attach_groups"] = vrf_attach_groups

        networks = await self._many(NetworkDB, fabric_id)
        if networks:
            net_list, net_attach_groups = await self._build_networks(networks)
            overlay["networks"] = net_list
            if net_attach_groups:
                overlay["network_attach_groups"] = net_attach_groups

        if overlay:
            vxlan["overlay"] = overlay

        # ── overlay_extensions ────────────────────────────────
        extensions: dict = {}

        vrf_lites = await self._many(VrfLiteExtensionDB, fabric_id)
        if vrf_lites:
            extensions["vrf_lite"] = [_row_to_dict(vl) for vl in vrf_lites]

        route_control = await self._build_route_control(fabric_id)
        if route_control:
            extensions["route_control"] = route_control

        if extensions:
            vxlan["overlay_extensions"] = extensions

        # ── policy ────────────────────────────────────────────
        policy_sec: dict = {}

        policies = await self._many(PolicyDB, fabric_id)
        if policies:
            policy_sec["policies"] = [_row_to_dict(p) for p in policies]

        groups = await self._many(PolicyGroupDB, fabric_id)
        if groups:
            policy_sec["groups"] = [_row_to_dict(g) for g in groups]

        if policy_sec:
            vxlan["policy"] = policy_sec

        return {"vxlan": vxlan}

    # ── helpers ───────────────────────────────────────────────

    async def _one(self, model, fabric_id: UUID, *, pk: str = "fabric_id"):
        """Fetch a single row by fabric_id (or by primary key if pk='id')."""
        if pk == "id":
            stmt = select(model).where(model.id == fabric_id)
        else:
            stmt = select(model).where(model.fabric_id == fabric_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _many(self, model, fabric_id: UUID) -> list:
        """Fetch all rows for a fabric."""
        stmt = select(model).where(model.fabric_id == fabric_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _interfaces_for_fabric(self, fabric_id: UUID) -> dict[str, list[dict]]:
        """Fetch all interfaces across all switches in the fabric.

        Returns a dictionary mapping switch_name to a list of interface dicts,
        to be nested under each switch.
        """
        stmt = (
            select(InterfaceDB, SwitchDB.name.label("switch_name"))
            .join(SwitchDB, InterfaceDB.switch_id == SwitchDB.id)
            .where(SwitchDB.fabric_id == fabric_id)
        )
        result = await self.db.execute(stmt)
        interfaces: dict[str, list[dict]] = {}
        for row in result:
            iface = row[0]
            switch_name = row[1]
            d = _row_to_dict(iface, skip=_SKIP | {"switch_id"})
            # Flatten type_config into top level
            tc = d.pop("type_config", None)
            if tc and isinstance(tc, dict):
                d.update(tc)
            interfaces.setdefault(switch_name, []).append(d)
        return interfaces

    async def _build_vrfs(self, vrfs: list) -> tuple[list[dict], list[dict]]:
        """Build VRF dicts and extract switch attachments into groups."""
        result = []
        attach_groups = []
        for vrf in vrfs:
            d = _row_to_dict(vrf)
            # Fetch switch attachments
            stmt = select(VrfSwitchAttachmentDB).where(
                VrfSwitchAttachmentDB.vrf_id == vrf.id
            )
            res = await self.db.execute(stmt)
            attachments = list(res.scalars().all())
            if attachments:
                group_name = f"{vrf.name}_attach"
                d["vrf_attach_group"] = group_name
                
                switches_data = []
                for a in attachments:
                    att_dict = _row_to_dict(a, skip=_SKIP | {"vrf_id"})
                    switches_data.append(att_dict)
                
                attach_groups.append({
                    "name": group_name,
                    "switches": switches_data
                })
            result.append(d)
        return result, attach_groups

    async def _build_networks(self, networks: list) -> tuple[list[dict], list[dict]]:
        """Build network dicts and extract switch attachments into groups."""
        result = []
        attach_groups = []
        for net in networks:
            d = _row_to_dict(net)
            stmt = select(NetworkSwitchAttachmentDB).where(
                NetworkSwitchAttachmentDB.network_id == net.id
            )
            res = await self.db.execute(stmt)
            attachments = list(res.scalars().all())
            if attachments:
                group_name = f"{net.name}_attach"
                d["attach_group_name"] = group_name
                
                switches_data = []
                for a in attachments:
                    att_dict = _row_to_dict(a, skip=_SKIP | {"network_id"})
                    switches_data.append(att_dict)
                
                attach_groups.append({
                    "name": group_name,
                    "switches": switches_data
                })
            result.append(d)
        return result, attach_groups

    async def _build_route_control(self, fabric_id: UUID) -> dict:
        """Build the route_control section."""
        rc: dict = {}
        for key, model in [
            ("ipv4_prefix_lists", Ipv4PrefixListDB),
            ("ipv6_prefix_lists", Ipv6PrefixListDB),
            ("standard_community_lists", StandardCommunityListDB),
            ("extended_community_lists", ExtendedCommunityListDB),
            ("ip_as_path_access_lists", IpAsPathAccessListDB),
            ("route_maps", RouteMapDB),
            ("ip_acls", IpAclDB),
            ("mac_lists", MacListDB),
            ("object_groups", ObjectGroupDB),
            ("time_ranges", TimeRangeDB),
        ]:
            rows = await self._many(model, fabric_id)
            if rows:
                rc[key] = [_row_to_dict(r) for r in rows]
        return rc