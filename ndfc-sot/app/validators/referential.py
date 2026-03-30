"""Cross-entity referential integrity validators."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.fabric import FabricDB
from app.db_models.network import NetworkDB
from app.db_models.switch import SwitchDB
from app.db_models.vrf import VrfDB
from app.exceptions import NotFoundError, ValidationError


async def validate_fabric_exists(db: AsyncSession, fabric_id: UUID) -> FabricDB:
    """Ensure a fabric exists, raise NotFoundError otherwise."""
    fabric = await db.get(FabricDB, fabric_id)
    if not fabric:
        raise NotFoundError(f"Fabric {fabric_id} not found")
    return fabric


async def validate_switch_exists(
    db: AsyncSession, fabric_id: UUID, hostname: str
) -> SwitchDB:
    """Ensure a switch exists in the given fabric."""
    result = await db.execute(
        select(SwitchDB).where(
            SwitchDB.fabric_id == fabric_id,
            SwitchDB.name == hostname,
        )
    )
    switch = result.scalars().first()
    if not switch:
        raise NotFoundError(
            f"Switch '{hostname}' not found in fabric {fabric_id}",
            error_code="DEPENDENCY_NOT_FOUND"
        )
    return switch


async def validate_switches_exist(
    db: AsyncSession, fabric_id: UUID, hostnames: list[str]
) -> list[SwitchDB]:
    """Ensure all switches in the list exist in the fabric."""
    switches = []
    for hostname in hostnames:
        sw = await validate_switch_exists(db, fabric_id, hostname)
        switches.append(sw)
    return switches


async def validate_vrf_exists(
    db: AsyncSession, fabric_id: UUID, vrf_name: str
) -> VrfDB:
    """Ensure a VRF exists in the given fabric."""
    result = await db.execute(
        select(VrfDB).where(
            VrfDB.fabric_id == fabric_id,
            VrfDB.name == vrf_name,
        )
    )
    vrf = result.scalars().first()
    if not vrf:
        raise NotFoundError(
            f"VRF '{vrf_name}' not found in fabric {fabric_id}"
        )
    return vrf


async def validate_network_exists(
    db: AsyncSession, fabric_id: UUID, network_name: str
) -> NetworkDB:
    """Ensure a network exists in the given fabric."""
    result = await db.execute(
        select(NetworkDB).where(
            NetworkDB.fabric_id == fabric_id,
            NetworkDB.name == network_name,
        )
    )
    network = result.scalars().first()
    if not network:
        raise NotFoundError(
            f"Network '{network_name}' not found in fabric {fabric_id}"
        )
    return network


async def validate_vlan_not_duplicate(
    db: AsyncSession, fabric_id: UUID, vlan_id: int, exclude_network_id: UUID | None = None
) -> None:
    """Ensure a VLAN ID is not already used in the fabric."""
    query = select(NetworkDB).where(
        NetworkDB.fabric_id == fabric_id,
        NetworkDB.vlan_id == vlan_id,
    )
    if exclude_network_id:
        query = query.where(NetworkDB.id != exclude_network_id)
    result = await db.execute(query)
    existing = result.scalars().first()
    if existing:
        raise ValidationError(
            f"VLAN {vlan_id} is already used by network '{existing.name}' "
            f"in fabric {fabric_id}"
        )


async def validate_vni_not_duplicate(
    db: AsyncSession,
    fabric_id: UUID,
    vni: int,
    exclude_id: UUID | None = None,
) -> None:
    """Ensure a VNI is not already used (check both VRFs and networks)."""
    # Check VRFs
    vrf_query = select(VrfDB).where(
        VrfDB.fabric_id == fabric_id, VrfDB.vrf_id == vni
    )
    if exclude_id:
        vrf_query = vrf_query.where(VrfDB.id != exclude_id)
    result = await db.execute(vrf_query)
    if result.scalars().first():
        raise ValidationError(
            f"VNI {vni} is already used by a VRF in fabric {fabric_id}"
        )

    # Check Networks
    net_query = select(NetworkDB).where(
        NetworkDB.fabric_id == fabric_id, NetworkDB.network_id == vni
    )
    if exclude_id:
        net_query = net_query.where(NetworkDB.id != exclude_id)
    result = await db.execute(net_query)
    if result.scalars().first():
        raise ValidationError(
            f"VNI {vni} is already used by a network in fabric {fabric_id}"
        )